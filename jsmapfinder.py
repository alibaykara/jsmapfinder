#!/usr/bin/env python3
"""
jsmapfinder - JavaScript Source Maps Enumeration Tool
Python implementasyonu

Gerekli kütüphaneler:
pip install requests beautifulsoup4 jsbeautifier

Kullanım:
  python jsmapfinder.py -u https://example.com
  python jsmapfinder.py -f urls.txt -v
  python jsmapfinder.py -u https://example.com -H "User-Agent: MyBot"
  python jsmapfinder.py -u https://example.com --beautify --output results/
"""

import argparse
import re
import sys
import os
import json
from urllib.parse import urljoin, urlparse
from typing import List, Set, Optional, Dict
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import jsbeautifier


class Colors:
    """Terminal renk kodları"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class JSMapFinder:
    def __init__(self, headers: dict = None, verbose: bool = False, beautify: bool = False, output_dir: str = None):
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.verbose = verbose
        self.beautify = beautify
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Output dizinini oluştur
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, 'sourcemaps'), exist_ok=True)
            os.makedirs(os.path.join(self.output_dir, 'sources'), exist_ok=True)
        
    def log(self, message: str, color: str = Colors.RESET):
        """Renkli log yazdır"""
        print(f"{color}{message}{Colors.RESET}")
    
    def extract_js_urls(self, url: str) -> Set[str]:
        """HTML sayfasından JavaScript URL'lerini çıkar"""
        js_urls = set()
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Script tag'lerinden src'leri al
            for script in soup.find_all('script', src=True):
                js_url = urljoin(url, script['src'])
                js_urls.add(js_url)
            
            if self.verbose:
                self.log(f"  [*] {len(js_urls)} JavaScript dosyası bulundu", Colors.BLUE)
                
        except Exception as e:
            self.log(f"  [!] HTML parse hatası: {str(e)}", Colors.RED)
            
        return js_urls
    
    def check_sourcemap_in_js(self, js_url: str) -> Optional[str]:
        """JavaScript dosyasında source map referansı kontrol et"""
        try:
            response = self.session.get(js_url, timeout=10)
            response.raise_for_status()
            content = response.text
            
            # sourceMappingURL pattern'i ara
            # //# sourceMappingURL=file.js.map
            # //@ sourceMappingURL=file.js.map (eski format)
            patterns = [
                r'//[@#]\s*sourceMappingURL=(.+?)(?:\s|$)',
                r'/\*[@#]\s*sourceMappingURL=(.+?)\s*\*/'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, content)
                if match:
                    map_url = match.group(1).strip()
                    # Relatif URL'yi absolute yap
                    full_map_url = urljoin(js_url, map_url)
                    return full_map_url
            
            # Direkt .js.map uzantısını dene
            if js_url.endswith('.js'):
                potential_map = js_url + '.map'
                if self.check_url_exists(potential_map):
                    return potential_map
                    
        except Exception as e:
            if self.verbose:
                self.log(f"  [!] JS kontrol hatası ({js_url}): {str(e)}", Colors.RED)
                
        return None
    
    def check_url_exists(self, url: str) -> bool:
        """URL'nin erişilebilir olup olmadığını kontrol et"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def verify_sourcemap(self, map_url: str) -> bool:
        """Source map dosyasının geçerli olup olmadığını kontrol et"""
        try:
            response = self.session.get(map_url, timeout=10)
            if response.status_code == 200:
                # JSON formatında olmalı ve version field'ı içermeli
                data = response.json()
                return 'version' in data and 'sources' in data
        except:
            pass
        return False
    
    def save_sourcemap(self, map_url: str, map_data: dict, base_name: str):
        """Source map'i kaydet ve içindeki kaynak dosyaları çıkar"""
        if not self.output_dir:
            return
        
        try:
            # Source map'i kaydet
            map_file = os.path.join(self.output_dir, 'sourcemaps', f'{base_name}.map')
            with open(map_file, 'w', encoding='utf-8') as f:
                json.dump(map_data, f, indent=2)
            
            if self.verbose:
                self.log(f"    [*] Source map kaydedildi: {map_file}", Colors.BLUE)
            
            # Source içeriklerini çıkar ve kaydet
            if 'sourcesContent' in map_data and map_data['sourcesContent']:
                sources = map_data.get('sources', [])
                contents = map_data['sourcesContent']
                
                for i, (source_path, content) in enumerate(zip(sources, contents)):
                    if content:
                        # Güvenli dosya adı oluştur
                        safe_name = source_path.replace('/', '_').replace('\\', '_').replace('..', '_')
                        source_file = os.path.join(self.output_dir, 'sources', f'{base_name}_{safe_name}')
                        
                        # JavaScript ise beautify et
                        if self.beautify and (source_path.endswith('.js') or source_path.endswith('.jsx') or source_path.endswith('.ts')):
                            try:
                                beautified = jsbeautifier.beautify(content)
                                content = beautified
                                if self.verbose:
                                    self.log(f"    [*] Beautified: {safe_name}", Colors.BLUE)
                            except Exception as e:
                                if self.verbose:
                                    self.log(f"    [!] Beautify hatası ({safe_name}): {str(e)}", Colors.YELLOW)
                        
                        # Dosyayı kaydet
                        with open(source_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                
                self.log(f"    [✓] {len(contents)} kaynak dosya çıkarıldı", Colors.GREEN)
            
        except Exception as e:
            self.log(f"    [!] Kayıt hatası: {str(e)}", Colors.RED)
    
    def scan_url(self, url: str) -> List[Dict[str, any]]:
        """Tek bir URL'yi tarayıp source map'leri bul"""
        found_maps = []
        
        self.log(f"\n[+] Taranıyor: {url}", Colors.BOLD)
        
        # URL'den JavaScript dosyalarını çıkar
        js_urls = self.extract_js_urls(url)
        
        if not js_urls:
            self.log("  [!] JavaScript dosyası bulunamadı", Colors.YELLOW)
            return found_maps
        
        # Her JS dosyasını kontrol et
        for idx, js_url in enumerate(js_urls):
            if self.verbose:
                self.log(f"  [*] Kontrol ediliyor: {js_url}", Colors.BLUE)
            
            map_url = self.check_sourcemap_in_js(js_url)
            
            if map_url:
                # Source map'i doğrula ve içeriğini al
                try:
                    response = self.session.get(map_url, timeout=10)
                    if response.status_code == 200:
                        map_data = response.json()
                        
                        if 'version' in map_data and 'sources' in map_data:
                            self.log(f"  [✓] Source map bulundu: {map_url}", Colors.GREEN)
                            
                            # Source map bilgilerini kaydet
                            map_info = {
                                'url': map_url,
                                'js_url': js_url,
                                'sources_count': len(map_data.get('sources', [])),
                                'has_content': 'sourcesContent' in map_data
                            }
                            found_maps.append(map_info)
                            
                            # Dosyalara kaydet
                            if self.output_dir:
                                base_name = f"map_{idx+1}_{urlparse(url).netloc}"
                                self.save_sourcemap(map_url, map_data, base_name)
                        else:
                            if self.verbose:
                                self.log(f"  [!] Geçersiz source map: {map_url}", Colors.YELLOW)
                except Exception as e:
                    if self.verbose:
                        self.log(f"  [!] Source map parse hatası: {str(e)}", Colors.RED)
        
        if not found_maps:
            self.log("  [!] Source map bulunamadı", Colors.YELLOW)
        else:
            self.log(f"  [✓] Toplam {len(found_maps)} source map bulundu", Colors.GREEN)
            
        return found_maps
    
    def scan_urls_from_file(self, file_path: str) -> dict:
        """Dosyadan URL'leri okuyup tara"""
        results = {}
        
        try:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            self.log(f"[*] {len(urls)} URL dosyadan okundu", Colors.BLUE)
            
            # Paralel tarama için ThreadPoolExecutor kullan
            with ThreadPoolExecutor(max_workers=5) as executor:
                future_to_url = {executor.submit(self.scan_url, url): url for url in urls}
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        maps = future.result()
                        results[url] = maps
                    except Exception as e:
                        self.log(f"[!] Hata ({url}): {str(e)}", Colors.RED)
                        results[url] = []
                        
        except FileNotFoundError:
            self.log(f"[!] Dosya bulunamadı: {file_path}", Colors.RED)
            sys.exit(1)
        except Exception as e:
            self.log(f"[!] Dosya okuma hatası: {str(e)}", Colors.RED)
            sys.exit(1)
            
        return results
    
    def print_summary(self, results: dict):
        """Özet rapor yazdır"""
        print("\n" + "="*60)
        self.log("ÖZET RAPOR", Colors.BOLD)
        print("="*60)
        
        total_urls = len(results)
        urls_with_maps = sum(1 for maps in results.values() if maps)
        total_maps = sum(len(maps) for maps in results.values())
        
        # Toplam kaynak dosya sayısı
        total_sources = 0
        sources_with_content = 0
        for maps in results.values():
            for map_info in maps:
                total_sources += map_info.get('sources_count', 0)
                if map_info.get('has_content', False):
                    sources_with_content += map_info.get('sources_count', 0)
        
        print(f"Taranan URL sayısı: {total_urls}")
        print(f"Source map bulunan URL: {urls_with_maps}")
        print(f"Toplam source map: {total_maps}")
        print(f"Toplam kaynak dosya: {total_sources}")
        print(f"İçerik bulunan kaynak: {sources_with_content}")
        
        if self.output_dir:
            print(f"\nDosyalar kaydedildi: {os.path.abspath(self.output_dir)}")
        
        print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='JavaScript Source Maps Enumeration Tool (Python)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python jsmapfinder.py -u https://example.com
  python jsmapfinder.py -f urls.txt
  python jsmapfinder.py -u https://example.com -H "Cookie: session=abc" -v
  python jsmapfinder.py -u https://example.com --beautify --output results/
  python jsmapfinder.py -f urls.txt -b -o results/ -v
        """
    )
    
    parser.add_argument('-u', '--url', help='Taranacak hedef URL')
    parser.add_argument('-f', '--file', help='URL listesi içeren dosya')
    parser.add_argument('-H', '--header', action='append', 
                       help='Özel HTTP header (örn: "User-Agent: custom-agent")')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Detaylı çıktı')
    parser.add_argument('-b', '--beautify', action='store_true',
                       help='JavaScript kodlarını güzelleştir (beautify)')
    parser.add_argument('-o', '--output', metavar='DIR',
                       help='Source map ve kaynak dosyaları kaydetme dizini')
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 2.0.0')
    
    args = parser.parse_args()
    
    # En az bir parametre gerekli
    if not args.url and not args.file:
        parser.print_help()
        sys.exit(1)
    
    # Custom header'ları parse et
    headers = {}
    if args.header:
        for header in args.header:
            if ':' in header:
                key, value = header.split(':', 1)
                headers[key.strip()] = value.strip()
    
    # JSMapFinder instance oluştur
    finder = JSMapFinder(
        headers=headers if headers else None, 
        verbose=args.verbose,
        beautify=args.beautify,
        output_dir=args.output
    )
    
    # Tek URL taraması
    if args.url:
        maps = finder.scan_url(args.url)
        results = {args.url: maps}
    # Dosyadan çoklu URL taraması
    else:
        results = finder.scan_urls_from_file(args.file)
    
    # Özet rapor
    finder.print_summary(results)


if __name__ == '__main__':
    main()
