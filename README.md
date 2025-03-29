# ChatBot-UI
İlk olarak codellama:7b modelini indirip kullanabilmek için ollama uygulamasını indirmeniz gerekicek 


`https://ollama.com/download/windows`

Daha sonra CMD komut satırına veya PowerShell'e şu komutu yazıp çalıştırın bu komut modeli indirecektir


`ollama pull codellama:7b` => bu işlem biraz zaman alabilir

`ollama list` => daha sonra bu kodu çalıştırıp yüklendiğini kontrol edebilirsiniz

eğer indirilen modeli komut satırından test etmek istiyorsan => `ollama run codellama:7b` 

Bu komut çalıştırıldığında terminalde ">" şeklinde bir giriş satırı göreceksin. Buraya bir Python sorusu yaz ve modelin cevap vermesini bekle.

Bu işlemleri yaptıktan sonra anaconda promt'a gelip kullandığın Environments aktif edip şu kütüphaneleri yüklemelisin


`pip install ollama` --- `pip install pyqt6`

Bu kütüphaneleri yükledikten sonra kodu yazmaya başlayabilirsin

