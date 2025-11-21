#JSMapFinder - JavaScript Source Maps Enumeration Tool
````markdown
# JSMapFinder - JavaScript Source Maps Enumeration Tool

JSMapFinder, web sitelerindeki JavaScript dosyalarını tarayarak **Source Map** (Kaynak Haritası) dosyalarını tespit eden, indiren ve orijinal kaynak kodlarını (unminified code) çıkaran Python tabanlı bir araçtır.

Siber güvenlik araştırmacıları, bug bounty avcıları ve geliştiriciler için; sıkıştırılmış (minified) JavaScript kodlarının orijinal hallerine erişmek ve potansiyel hassas verileri veya mantık hatalarını analiz etmek amacıyla tasarlanmıştır.

## 🚀 Özellikler

* **Otomatik Tespit:** HTML içindeki `<script>` etiketlerini tarar ve `.map` dosyalarını bulur.
* **Akıllı Algılama:** Hem `sourceMappingURL` referanslarını kontrol eder hem de yaygın isimlendirme standartlarına göre tahmin yürütür.
* **Kod Çıkarma:** Source Map dosyası içerisindeki `sourcesContent` verisini kullanarak orijinal kaynak kodlarını diske kaydeder.
* **JS Beautifier:** Çıkarılan kodları okunabilir hale getirmek için otomatik formatlama (beautify) seçeneği sunar.
* **Çoklu Tarama:** URL listesi vererek birden fazla hedefi aynı anda (multi-threading ile) tarayabilirsiniz.
* **Renkli Çıktı:** Terminal üzerinde detaylı ve renkli durum raporu sunar.

## 📦 Kurulum

Bu aracı kullanmak için Python 3.x gereklidir.

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/alibaykara/jsmapfinder.git
   cd jsmapfinder
   pip install -r requirements.txt --break-system-packages
````

2.  Gerekli kütüphaneleri yükleyin:
    ```bash
    pip install -r requirements.txt --break-system-packages
    ```

## 🛠 Kullanım

En basit haliyle bir URL taramak için:

```bash
python jsmapfinder.py -u https://example.com -b -o results/
```

### Parametreler

| Parametre | Kısa | Açıklama |
|-----------|------|----------|
| `--url` | `-u` | Taranacak hedef web sitesi URL'si. |
| `--file` | `-f` | İçinde URL listesi olan dosya yolu (toplu tarama). |
| `--output`| `-o` | Sonuçların kaydedileceği klasör adı. |
| `--beautify`| `-b` | Çıkarılan JS kodlarını güzelleştirir (formatlar). |
| `--verbose` | `-v` | Daha detaylı çıktı gösterir. |
| `--header` | `-H` | Özel HTTP başlığı ekler (örn: Cookie veya User-Agent). |

### Örnek Senaryolar

**1. Kaynak kodları çıkarıp klasöre kaydetme ve formatlama:**
Bu komut kaynak kodları `sonuclar/` klasörüne indirir ve kodları okunabilir hale getirir.

```bash
python jsmapfinder.py -u https://example.com --output sonuclar/ --beautify
```

**2. Bir dosyadaki tüm URL'leri tarama:**

```bash
python jsmapfinder.py -f urllistesi.txt -v
```

**3. Özel Cookie veya User-Agent ile tarama:**
Kimlik doğrulama gerektiren sayfalar için:

```bash
python jsmapfinder.py -u https://panel.example.com -H "Cookie: session=xyz123"
```

## 📂 Çıktı Yapısı

Eğer `-o` parametresi kullanılırsa, araç şu yapıda klasörler oluşturur:

```text
output_dir/
├── sourcemaps/      # İndirilen .map dosyaları (JSON formatında)
└── sources/         # Source map içinden çıkarılan orijinal kod dosyaları
```

## ⚠️ Yasal Uyarı

Bu araç yalnızca yasal ve izinli güvenlik testleri veya eğitim amaçlı kullanım içindir. İzniniz olmayan sistemlerde kullanmak yasa dışı olabilir. Geliştirici, bu aracın kötüye kullanımından sorumlu tutulamaz.

## 🤝 Katkıda Bulunma

Hataları bildirmek veya özellik eklemek isterseniz, lütfen bir "Issue" açın veya "Pull Request" gönderin.

```text
requests
beautifulsoup4
jsbeautifier
argparse
```
