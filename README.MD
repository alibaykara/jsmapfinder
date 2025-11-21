Mükemmel! ✨ jsbeautifier kütüphanesini ekledim ve bir sürü yeni özellik ekledim:
🎨 Yeni Özellikler
1. JavaScript Beautifier

Minified/sıkıştırılmış JS kodlarını güzel, okunabilir formata dönüştürür
-b veya --beautify parametresi ile aktif edilir

2. Source Map İçeriklerini Kaydetme

Source map'lerdeki orijinal kaynak kodları çıkarır
-o veya --output parametresi ile dizin belirtilir
Otomatik klasör yapısı: sourcemaps/ ve sources/

3. Gelişmiş Raporlama

Kaç kaynak dosya bulundu
Hangilerinde içerik var
Dosyalar nereye kaydedildi

📦 Güncel Kurulum
bash# Tüm kütüphaneleri yükle
pip install requests beautifulsoup4 jsbeautifier
🚀 Yeni Kullanım Örnekleri
bash# Basit tarama
python jsmapfinder.py -u https://example.com

# Source map'leri kaydet ve beautify et
python jsmapfinder.py -u https://example.com -b -o results/

# Toplu tarama + beautify + verbose
python jsmapfinder.py -f urls.txt -b -o output/ -v

# Custom header ile + tüm özellikler
python jsmapfinder.py -u https://example.com \
  -H "User-Agent: MyBot" \
  -H "Cookie: session=abc123" \
  -b -o results/ -v
```

## 📁 Çıktı Yapısı
```
results/
├── sourcemaps/          # Source map JSON dosyaları
│   ├── map_1_example.com.map
│   └── map_2_example.com.map
└── sources/            # Çıkarılmış kaynak kodlar (beautified)
    ├── map_1_webpack_bootstrap.js
    ├── map_1_src_components_App.jsx
    └── map_2_main.bundle.js
Artık tool sadece source map bulmakla kalmıyor, orijinal kaynak kodları da çıkarıp güzelleştiriyor! 🎯
