import numpy as np
import urllib.request
import os
import cv2
cv2.__file__
import face_recognition
import sqlite3
import datetime
from win32api import GetSystemMetrics
import sys
import time

class veritabani():
    def __init__(self,veritabani_ismi):
        self.veritabani_ismi=veritabani_ismi
        self.tabloyu_olustur()

    def butun_sonuclari_ver(self):
        sonuc = self.sorguyu_gerceklestir("select * from tbl_takip",1)
        array = []
        for row in sonuc:
            array.append(row)
        self.conn.close()
        return(array)

    def butun_bulunan_yuzleri_kontrollu_ekle(self,bulunanlar,kamera_ismi,tarih):
        for bulunan in bulunanlar:
            self.takip_sistemine_yenisini_ekle(bulunan,kamera_ismi,tarih)#her kisiyi kontrollu ekleme islemi

    def takip_sistemine_yenisini_ekle(self,dizi,kamera_ismi,tarih):
        (tbl_takip_id,kackezgoruntelenmis) = self.isimli_kisi_sistemde_mevcut_mu(dizi[0],kamera_ismi,tarih)
        if(tbl_takip_id == 0):
            self.sorguyu_gerceklestir("INSERT INTO tbl_takip(isim,kamera_ismi,tarih,ilk_goruntulenme,kac_kare_goruntulenme) "+
                                      "VALUES ('{}','{}','{}',{},{})"
                                      .format(dizi[0],kamera_ismi,tarih,dizi[1],dizi[2]))
        else:
            self.sorguyu_gerceklestir("UPDATE tbl_takip SET kac_kare_goruntulenme='{}' WHERE id={}".format(dizi[2]+kackezgoruntelenmis,tbl_takip_id))

    def kullanicinin_kackarede_oldugunu_ver(self,isim,kamera_ismi,tarih):
        kackezgoruntelenmis = 0
        sorgu ="select * from tbl_takip where isim='{}' and kamera_ismi='{}' and tarih='{}'".format(isim,kamera_ismi,tarih)
        sonuc = self.sorguyu_gerceklestir(sorgu,1)
        for i in sonuc:
            kackezgoruntelenmis = int(i[5])
        return(kackezgoruntelenmis)

    def isimli_kisi_sistemde_mevcut_mu(self,isim,kamera_ismi, tarih):#bir kişinin sistemde olup olmadığını buluyor
        kackezgoruntelenmis = 0
        sorgu ="select * from tbl_takip where isim='{}' and kamera_ismi='{}' and tarih='{}'".format(isim,kamera_ismi,tarih)
        sonuc = self.sorguyu_gerceklestir(sorgu,1)
        sonuc_id=0
        for i in sonuc:
            sonuc_id=int(i[0])
            kackezgoruntelenmis = int(i[5])
        return(sonuc_id,kackezgoruntelenmis)

    def sorguyu_gerceklestir(self,sorgu,type=0):#her sorgu işleminde dinamik bir yapı
        self.conn = sqlite3.connect(self.veritabani_ismi)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)#eğer bir yerde sorgu sonucunu yazdırmak istiyor isek, close() demeden önce yapmalıyız, bunu yapmak içinde type i belirtmek yeterli olacaktır
        self.conn.commit()
        self.conn.close()
        return(result)

    def tabloyu_olustur(self):#tablo mevcut da yok ise yenisini oluşturuyor
        self.sorguyu_gerceklestir("CREATE TABLE IF NOT EXISTS "+
                                      "tbl_takip("+
                                          "id INTEGER PRIMARY KEY autoincrement,"+
                                          "isim varchar(100),"+
                                          "kamera_ismi varchar(100),"+
                                          "tarih varchar(100),"+
                                          "ilk_goruntulenme int(6),"+
                                          "kac_kare_goruntulenme int(6)"+
                                      ")")

class kamera_baslat():
    def __init__(self,resimyolu,ip_adresleri,veritabani_ismi):
        self.resimyolu = resimyolu
        self.ip_adresleri = ip_adresleri
        self.baslangic_zaman = "18:00"
        self.veritabani_ismi = veritabani_ismi
        self.istenilen_kare_sayisinda_kabul = 5
        self.kacinci_saniyede_veritabani_guncellensin = 5
        self.bulunan_isimler = []
        self.faceCascade = cv2.CascadeClassifier('web/data/xml/haarcascade_frontalface_alt.xml')

        self.resim_yolundaki_yuzleri_bul()
        self.goruntuleri_izle()

    def veritabanini_guncelle(self,veritabani_ismi,bilgi,kamera_ismi,tarih):
        a = veritabani(veritabani_ismi)
        a.butun_bulunan_yuzleri_kontrollu_ekle(bilgi,kamera_ismi,tarih)

    def kullanicinin_kackere_goruntulendigi(self,veritabani_ismi,bilgi,kamera_ismi,tarih):
        a = veritabani(veritabani_ismi)
        return a.kullanicinin_kackarede_oldugunu_ver(bilgi,kamera_ismi,tarih)

    def isim_kayitli_mi(self,bulunan_isim):
        kayitli_mi=False
        i=0
        for isim in self.bulunan_isimler:
            if(isim[0] == bulunan_isim):
                kayitli_mi=True
                self.bulunan_isimler[i][2]+=1#kisinin istenilen kare sayisi kadar bulundugunda doğruluğunun kabulu
                break
            i+=1
        return(kayitli_mi)

    def frame_duzenle(self,frame_old,frame_sayisi):
        frame = cv2.resize(frame_old, (0, 0), fx=0.80, fy=0.80)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bulunan_yuzler = self.faceCascade.detectMultiScale(gray, 1.3, 5)
        tehlike_ismi="Tehlike !"

        for (x, y, w, h) in bulunan_yuzler:
            yuz_frame_old = frame[y-20:y+h+20,x-20:x+w+20]
            try:
                yuz_frame = cv2.resize(yuz_frame_old, (200, 200))
            except cv2.error as e:
                yuz_frame=yuz_frame_old

            bulunan_isim=""
            bulunacak_face = face_recognition.face_encodings(yuz_frame)
            if(bulunacak_face):
                for siradaki_yuz in self.resim_yolundaki_yuzler:
                    face_object = face_recognition.compare_faces([self.resim_yolundaki_yuzler[siradaki_yuz]], bulunacak_face[0])
                    if(face_object[0]):
                        bulunan_isim=siradaki_yuz.split('.')[0]
                        if(self.isim_kayitli_mi(bulunan_isim)!=True):
                            self.bulunan_isimler.append([bulunan_isim,int(frame_sayisi/30),1])
                        break
            yazilacak_isim=tehlike_ismi
            rgb = (0, 0, 255)
            if(bulunan_isim!=""):
                rgb=(0, 255, 0)
                yazilacak_isim=bulunan_isim

            cv2.rectangle(frame, (x, y), (x+w, y+h), rgb, 2)
            cv2.rectangle(frame, (x, y+h+25), (x+w, y+h-10), rgb, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, yazilacak_isim, (x + 6, y+h +14), font, 1.0, (255, 255, 255), 1)
        return(frame)

    def goruntuleri_izle(self):
        frame_sayisi=1
        self.bulunan_isimler=[]
        goruntu_yolu=""
        #ip=self.ip_adresleri[0]
        #if("rtsp" in ip):
            #_cap = cv2.VideoCapture(ip)
        while(True):
            cikisyap=False
            ekranlar=0
            for ip in self.ip_adresleri:
                self.bulunan_isimler=[]
                if("@" in ip):
                    ip = ip[ip.find("@")+1:]
                goruntu_yolu = ip

                frame = None
                if("rtsp" in ip):
                    #_cap = cv2.VideoCapture(ip)
                    cap = cv2.VideoCapture(ip)
                    ret,frame = cap.read()
                else:

                    with urllib.request.urlopen(ip) as url:
                        imgResp = url.read()

                    imgNp = np.array(bytearray(imgResp),dtype=np.uint8)
                    if(len(imgNp)>0):
                        frame = cv2.imdecode(imgNp,-1)
                if(frame is not None):

                    frame = self.frame_duzenle(frame,frame_sayisi)

                    (height, width, channels) = frame.shape
                    alta_yazdir = 0
                    for bulunan in self.bulunan_isimler:
                        rgb_bulunan=(255, 255, 255)
                        if(bulunan[2]>=self.istenilen_kare_sayisinda_kabul):
                            rgb_bulunan=(0, 255, 0)
                        cv2.putText(frame, str(self.kullanicinin_kackere_goruntulendigi(self.veritabani_ismi,bulunan[0],goruntu_yolu,str(datetime.datetime.today().strftime('%d, %m %y'))))+" - "+goruntu_yolu+" - "+bulunan[0], (width - 500, 14 + alta_yazdir), cv2.FONT_HERSHEY_DUPLEX, 0.5, rgb_bulunan, 1)
                        alta_yazdir+=20
                    if(self.bulunan_isimler):
                        if(self.bulunan_isimler[0]):
                            self.veritabanini_guncelle(self.veritabani_ismi,self.bulunan_isimler,goruntu_yolu,str(datetime.datetime.today().strftime('%d, %m %y')))

                    #en_sayisi = self.ekran_en_sayisini_ver(len(self.ip_adresleri))#bu asama diger versiyonda yapılacaktır. Bu aşama 123,123 gibi aşağıya doğru giden bir sistem olacaktır.

                    ekran_eni = GetSystemMetrics(0)
                    ekran_boyu = GetSystemMetrics(1)
                    toplam_ekran_sayisi = len(self.ip_adresleri)

                    en_boy_orani = ekran_eni/ekran_boyu

                    frame_eni = int(ekran_eni/toplam_ekran_sayisi)
                    frame_boyu = int(frame_eni/en_boy_orani)

                    ekran_baslik_ismi = 'Kamera'+str(ekranlar)
                    cv2.moveWindow(ekran_baslik_ismi, ekranlar*frame_eni,0)

                    frame = cv2.resize(frame, (frame_eni, frame_boyu))
                    cv2.imshow(ekran_baslik_ismi, frame)


                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        cikisyap=True
                        break
                    ekranlar+=1
                else:
                    self.ip_adresleri.remove(ip)
                    cv2.destroyAllWindows()
                    if(len(self.ip_adresleri)<1):
                        cikisyap=True
                        break
            if(cikisyap):
                break

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame_sayisi+=1
        cv2.destroyAllWindows()

    def ekran_en_sayisini_ver(self,ekran_sayisi):
        duzenek = {
                    2:2,3:2,4:2,
                    5:3,6:3,7:3,8:3,9:3,
                    10:4,11:4,12:4,13:4,14:4,15:4,16:4
                }
        return duzenek[ekran_sayisi]

    def resim_yolundaki_yuzleri_bul(self):
        print("resimler",self.resimyolu)
        resimler = os.listdir(self.resimyolu)
        yuzler = {}
        for resim in resimler:
            tur = resim.split('.')[1]
            if(tur == "jpg" or tur == "jpeg"):
                if(face_recognition.face_encodings(face_recognition.load_image_file(self.resimyolu+"/"+resim))):
                    yuzler[resim]=face_recognition.face_encodings(face_recognition.load_image_file(self.resimyolu+"/"+resim))[0]
        self.resim_yolundaki_yuzler = yuzler

class rapor_datagrid_view():
    def __init__(self,veritabani_ismi,aranan):
        self.veritabani_ismi = veritabani_ismi
        self.aranan = aranan
        self.createTable()

    def createTable(self):
        a = veritabani(self.veritabani_ismi)
        results = a.sorguyu_gerceklestir("select * from tbl_takip where isim like '%"+self.aranan+"%'",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows

class pc_kamerasindan_resim_cek():
    def __init__(self, resim_yolu, resimismi, cikisyap):
        self.resim_yolu = resim_yolu
        self.cekilen_resim = None
        self.resim_ismi = resimismi
        self.resim_cekimi_hatali_degil_mi = True
        self.cikisyap = cikisyap

    def ResimCekmekIcinClick(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            resim_ismi = self.resim_ismi
            cv2.imwrite(self.resim_yolu+"/"+resim_ismi.strip()+".jpg",self.cekilen_resim)
            self.resim_cekimi_hatali_degil_mi=False

    def btn_ResimCekAcilClick(self):
        self.resim_cekimi_hatali_degil_mi=True
        vcap = cv2.VideoCapture(0)
        while(True and self.resim_cekimi_hatali_degil_mi):
            ret1, frame1 = vcap.read()
            frame_isim = "Resim Cekme - Fare 1 Cift Tiklanma"
            self.cekilen_resim=frame1
            cv2.setMouseCallback(frame_isim,self.ResimCekmekIcinClick)
            cv2.imshow(frame_isim,frame1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.cikisyap=True
                break
        cv2.destroyAllWindows()

class kayitli_kameradan_resim_cekme():
    def __init__(self, resim_yolu, resimismi, ip):
        self.resim_yolu = resim_yolu
        self.cekilen_resim = None
        self.resim_ismi = resimismi
        self.ip = ip
        self.resim_cekimi_hatali_degil_mi = True
        self.cikisyap = False

    def ResimCekmekIcinClick(self,event,x,y,flags,param):
        if event == cv2.EVENT_LBUTTONDBLCLK:
            resim_ismi = self.resim_ismi
            cv2.imwrite(self.resim_yolu+"/"+resim_ismi.strip()+".jpg",self.cekilen_resim)
            self.resim_cekimi_hatali_degil_mi=False

    def btn_ResimCekAcilClick(self):
        frame_isim = "Kayitli Kameradan Resim Cekme - Fare 1 Cift Tiklanma"
        if("rtsp" in self.ip):
            self.resim_cekimi_hatali_degil_mi=True
            vcap = cv2.VideoCapture(self.ip)
            while(True and self.resim_cekimi_hatali_degil_mi):
                ret1, frame1 = vcap.read()
                self.cekilen_resim=frame1
                cv2.setMouseCallback(frame_isim,self.ResimCekmekIcinClick)
                cv2.imshow(frame_isim,frame1)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.cikisyap=True
                    break
            cv2.destroyAllWindows()
        else:
            self.resim_cekimi_hatali_degil_mi=True
            while(True and self.resim_cekimi_hatali_degil_mi):
                with urllib.request.urlopen(self.ip) as url:
                    imgResp = url.read()
                imgNp = np.array(bytearray(imgResp),dtype=np.uint8)
                if(len(imgNp)>0):
                    frame = cv2.imdecode(imgNp,-1)
                    self.cekilen_resim=frame
                    cv2.setMouseCallback(frame_isim,self.ResimCekmekIcinClick)
                    cv2.imshow(frame_isim, frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.cikisyap=True
                        break
            cv2.destroyAllWindows()

class kamera_veritabani():
    def __init__(self,kamera_veritabani):
        self.kamera_veritabani=kamera_veritabani
        self.tabloyu_olustur()

    def ekle(self,kullanici_adi,parola,ip_numarasi,allias, protokol, uzanti):
        self.sorguyu_gerceklestir("INSERT INTO tbl_kamera(kullanici_adi,parola,ip_numarasi,allias,protokol,uzanti) "+
                                     "VALUES ('{}','{}','{}','{}','{}','{}')"
                                     .format(kullanici_adi,parola,ip_numarasi,allias,protokol,uzanti))

    def sil(self,id):
        self.sorguyu_gerceklestir("DELETE FROM tbl_kamera WHERE id="+id)

    def sorguyu_gerceklestir(self,sorgu,type=0):#her sorgu işleminde dinamik bir yapı
        self.conn = sqlite3.connect(self.kamera_veritabani)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)#eğer bir yerde sorgu sonucunu yazdırmak istiyor isek, close() demeden önce yapmalıyız, bunu yapmak içinde type i belirtmek yeterli olacaktır
        self.conn.commit()
        self.conn.close()
        return(result)

    def tabloyu_olustur(self):#tablo mevcut da yok ise yenisini oluşturuyor
        self.sorguyu_gerceklestir("CREATE TABLE IF NOT EXISTS "+
                                      "tbl_kamera("+
                                          "id INTEGER PRIMARY KEY autoincrement,"+
                                          "kullanici_adi varchar(100),"+
                                          "parola varchar(100),"+
                                          "ip_numarasi varchar(100),"+
                                          "allias varchar(100),"+
                                          "protokol varchar(100),"+
                                          "uzanti varchar(100)"+
                                      ")")

class yeni_kamera_ekle():
    def __init__(self,kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti, kamera_veritabani):
        self.kullanici_adi = kullanici_adi
        self.parola = parola
        self.ip_numarasi = ip_numarasi
        self.allias = allias
        self.protokol = protokol
        self.uzanti = uzanti
        self.kamera_veritabani = kamera_veritabani
        self.kamera_ekle()

    def kamera_ekle(self):
        a = kamera_veritabani(self.kamera_veritabani)
        a.ekle(self.kullanici_adi,self.parola,self.ip_numarasi,self.allias, self.protokol, self.uzanti)

class mevcut_kamera_sil():
    def __init__(self, id, kamera_veritabani):
        self.id = id
        self.kamera_veritabani = kamera_veritabani
        self.kamera_sil()

    def kamera_sil(self):
        k = kamera_veritabani(self.kamera_veritabani)
        k.sil(self.id)

class tum_kameralari_ver():
    def __init__(self,kamera_veritabani):
        self.kamera_veritabani = kamera_veritabani
        self.createTable()

    def createTable(self):
        a = kamera_veritabani(self.kamera_veritabani)
        results = a.sorguyu_gerceklestir("select * from tbl_kamera",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows

class kamera_ara():
    def __init__(self,aranan,kamera_veritabani):
        self.aranan = aranan
        self.kamera_veritabani = kamera_veritabani
        self.createTable()

    def createTable(self):
        a = kamera_veritabani(self.kamera_veritabani)
        results = a.sorguyu_gerceklestir("select * from tbl_kamera where id like '%"+self.aranan+"%'",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows

class kamera_guncelle():
    def __init__(self,guncelle_id,kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti, kamera_veritabani):
        self.guncelle_id = guncelle_id
        self.kullanici_adi = kullanici_adi
        self.parola = parola
        self.ip_numarasi = ip_numarasi
        self.allias = allias
        self.protokol = protokol
        self.uzanti = uzanti
        self.kamera_veritabani = kamera_veritabani
        self.createTable()

    def createTable(self):
        a = kamera_veritabani(self.kamera_veritabani)
        results = a.sorguyu_gerceklestir("UPDATE tbl_kamera SET kullanici_adi='{}', parola='{}', ip_numarasi='{}', allias='{}', protokol='{}', uzanti='{}' WHERE id={}".format(self.kullanici_adi,self.parola,self.ip_numarasi,self.allias,self.protokol,self.uzanti,str(self.guncelle_id)))



class calisan_veritabani():
    def __init__(self,calisan_veritabani):
        self.calisan_veritabani=calisan_veritabani
        self.tabloyu_olustur()

    def ekle(self,ad,soyad,birim,kameralar):
        self.sorguyu_gerceklestir("INSERT INTO tbl_calisan(ad,soyad,birim,kameralar) "+
                                     "VALUES ('{}','{}','{}','{}')"
                                     .format(ad,soyad,birim,kameralar))

    def sil(self,id):
        self.sorguyu_gerceklestir("DELETE FROM tbl_calisan WHERE id="+id)

    def sorguyu_gerceklestir(self,sorgu,type=0):
        self.conn = sqlite3.connect(self.calisan_veritabani)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)
        self.conn.commit()
        self.conn.close()
        return(result)

    def tabloyu_olustur(self):
        self.sorguyu_gerceklestir("CREATE TABLE IF NOT EXISTS "+
                                      "tbl_calisan("+
                                          "id INTEGER PRIMARY KEY autoincrement,"+
                                          "ad varchar(100),"+
                                          "soyad varchar(100),"+
                                          "birim varchar(100),"+
                                          "kameralar varchar(150)"+
                                      ")")

class yeni_calisan_ekle():
    def __init__(self,ad, soyad, birim, kameralar, calisan_veritabani):
        self.ad = ad
        self.soyad = soyad
        self.birim = birim
        self.kameralar = kameralar
        self.calisan_veritabani = calisan_veritabani
        self.calisan_ekle()

    def calisan_ekle(self):
        a = calisan_veritabani(self.calisan_veritabani)
        a.ekle(self.ad, self.soyad, self.birim, self.kameralar)

class tum_calisanlari_ver():
    def __init__(self,calisan_veritabani):
        self.calisan_veritabani = calisan_veritabani
        self.createTable()

    def createTable(self):
        a = calisan_veritabani(self.calisan_veritabani)
        results = a.sorguyu_gerceklestir("select * from tbl_calisan",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows

class mevcut_calisan_sil():
    def __init__(self, id, calisan_veritabani):
        self.id = id
        self.calisan_veritabani = calisan_veritabani
        self.calisan_sil()

    def calisan_sil(self):
        k = calisan_veritabani(self.calisan_veritabani)
        k.sil(self.id)

class calisan_ara():
    def __init__(self,aranan,calisan_veritabani):
        self.aranan = aranan
        self.calisan_veritabani = calisan_veritabani
        self.createTable()

    def createTable(self):
        a = calisan_veritabani(self.calisan_veritabani)
        results = a.sorguyu_gerceklestir("select * from tbl_calisan where id like '%"+self.aranan+"%'",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows

class calisan_guncelle():
    def __init__(self,guncelle_id, ad, soyad, birim, guncel_kamera_list,calisan_veritabani):
        self.guncelle_id = guncelle_id
        self.ad = ad
        self.soyad = soyad
        self.birim = birim
        self.guncel_kamera_list = guncel_kamera_list
        self.calisan_veritabani = calisan_veritabani
        self.createTable()

    def createTable(self):
        a = calisan_veritabani(self.calisan_veritabani)
        results = a.sorguyu_gerceklestir("UPDATE tbl_calisan SET ad='{}', soyad='{}', birim='{}', kameralar='{}' WHERE id={}".format(self.ad, self.soyad, self.birim, self.guncel_kamera_list, str(self.guncelle_id)))



class pc_kamerasindan_anlik_goruntu_al():
    def __init__(self,anlik_goruntu_resim_yolu):
        self.anlik_goruntu_resim_yolu=anlik_goruntu_resim_yolu
        self.pc_kamerasindan_anlik_goruntu_al()

    def pc_kamerasindan_anlik_goruntu_al(self):
        self.goruntu='anlik_goruntu'
        camera = cv2.VideoCapture(0)
        return_value,image = camera.read()
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite(self.anlik_goruntu_resim_yolu+"/"+self.goruntu.strip()+".jpg",image)
        camera.release()
        return self.goruntu

class rtsp_kamerasindan_anlik_goruntu_al():
    def __init__(self,anlik_goruntu_resim_yolu,goruntu_alinacak_kamera):
        self.anlik_goruntu_resim_yolu=anlik_goruntu_resim_yolu
        self.goruntu_alinacak_kamera=goruntu_alinacak_kamera
        self.rtsp_kamerasindan_anlik_goruntu_al()

    def rtsp_kamerasindan_anlik_goruntu_al(self):
        print(cv2.__file__)
        self.goruntu='rtsp_kameradan_anlik_goruntu'
        camera = cv2.VideoCapture(self.goruntu_alinacak_kamera)
        return_value,image = camera.read()
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        cv2.imwrite(self.anlik_goruntu_resim_yolu+"/"+self.goruntu.strip()+".jpg",image)
        camera.release()
        return self.goruntu


class izleme_ekrani_icin_kameralardan_anlik_goruntu_al():
    def __init__(self,anlik_goruntu_resim_yolu,goruntu_alinacak_kamera,kamera):
        self.anlik_goruntu_resim_yolu=anlik_goruntu_resim_yolu
        self.goruntu_alinacak_kamera=goruntu_alinacak_kamera
        self.kamera=kamera
        self.izleme_ekrani_icin_kameralardan_anlik_goruntu_al()

    def izleme_ekrani_icin_kameralardan_anlik_goruntu_al(self):
        self.goruntu=self.kamera
        if("rtsp" in self.goruntu_alinacak_kamera):
            camera = cv2.VideoCapture(self.goruntu_alinacak_kamera)
            return_value,image = camera.read()
            gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            cv2.imwrite(self.anlik_goruntu_resim_yolu+"/"+self.goruntu.strip()+".jpg",image)
            camera.release()
        else:
            with urllib.request.urlopen(self.goruntu_alinacak_kamera) as url:
                imgResp = url.read()
            imgNp = np.array(bytearray(imgResp),dtype=np.uint8)
            if(len(imgNp)>0):
                frame = cv2.imdecode(imgNp,-1)
                cv2.imwrite(self.anlik_goruntu_resim_yolu+"/"+self.goruntu.strip()+".jpg",frame)
        return self.goruntu




class ziyaretci_veritabani():
    def __init__(self,ziyaretci_veritabani):
        self.ziyaretci_veritabani=ziyaretci_veritabani
        self.tabloyu_olustur()

    def ekle(self, tc, adi, soyadi, telefon, adres, kime_geldi):
        self.sorguyu_gerceklestir("INSERT INTO tbl_ziyaretci(tc, adi, soyadi, telefon, adres, kime_geldi) "+
                                     "VALUES ('{}','{}','{}','{}','{}','{}')"
                                     .format(tc, adi, soyadi, telefon, adres, kime_geldi))

    def sorguyu_gerceklestir(self,sorgu,type=0):#her sorgu işleminde dinamik bir yapı
        self.conn = sqlite3.connect(self.ziyaretci_veritabani)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)#eğer bir yerde sorgu sonucunu yazdırmak istiyor isek, close() demeden önce yapmalıyız, bunu yapmak içinde type i belirtmek yeterli olacaktır
        self.conn.commit()
        self.conn.close()
        return(result)

    def tabloyu_olustur(self):#tablo mevcut da yok ise yenisini oluşturuyor
        self.sorguyu_gerceklestir("CREATE TABLE IF NOT EXISTS "+
                                      "tbl_ziyaretci("+
                                          "id INTEGER PRIMARY KEY autoincrement,"+
                                          "tc varchar(100),"+
                                          "adi varchar(100),"+
                                          "soyadi varchar(100),"+
                                          "telefon varchar(100),"+
                                          "adres varchar(100),"+
                                          "kime_geldi varchar(100)"+
                                      ")")

class yeni_ziyaretci_ekle():
    def __init__(self, tc, adi, soyadi, telefon, adres, kime_geldi, ziyaretci_veritabani):
        self.tc = tc
        self.adi = adi
        self.soyadi = soyadi
        self.telefon = telefon
        self.adres = adres
        self.kime_geldi = kime_geldi
        self.ziyaretci_veritabani = ziyaretci_veritabani
        self.yeni_ziyaretci_ekle()

    def yeni_ziyaretci_ekle(self):
        a = ziyaretci_veritabani(self.ziyaretci_veritabani)
        a.ekle(self.tc, self.adi, self.soyadi, self.telefon, self.adres, self.kime_geldi)

class tum_ziyaretcileri_goster():
    def __init__(self,ziyaretci_veritabani):
        self.ziyaretci_veritabani = ziyaretci_veritabani
        self.createTable()

    def createTable(self):
        a = ziyaretci_veritabani(self.ziyaretci_veritabani)
        results = a.sorguyu_gerceklestir("select * from tbl_ziyaretci",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows



class veritabani_kayitli_ziyaretciler():
    def __init__(self,veritabani_ismi):
        self.veritabani_ismi=veritabani_ismi

    def sorguyu_gerceklestir(self,sorgu,type=0):#her sorgu işleminde dinamik bir yapı
        self.conn = sqlite3.connect(self.veritabani_ismi)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)#eğer bir yerde sorgu sonucunu yazdırmak istiyor isek, close() demeden önce yapmalıyız, bunu yapmak içinde type i belirtmek yeterli olacaktır
        self.conn.commit()
        self.conn.close()
        return(result)

class kayitli_ziyaretcileri_goster():
    def __init__(self,kayitli_ziyaretci_veritabani):
        self.kayitli_ziyaretci_veritabani = kayitli_ziyaretci_veritabani
        self.createTable()

    def createTable(self):
        a = veritabani_kayitli_ziyaretciler(self.kayitli_ziyaretci_veritabani)
        results = a.sorguyu_gerceklestir("select * from tbl_kayitli_ziyaretciler",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows

class veritabani_kayitli_olmayan_ziyaretciler():
    def __init__(self,veritabani_ismi):
        self.veritabani_ismi=veritabani_ismi

    def sorguyu_gerceklestir(self,sorgu,type=0):#her sorgu işleminde dinamik bir yapı
        self.conn = sqlite3.connect(self.veritabani_ismi)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)#eğer bir yerde sorgu sonucunu yazdırmak istiyor isek, close() demeden önce yapmalıyız, bunu yapmak içinde type i belirtmek yeterli olacaktır
        self.conn.commit()
        self.conn.close()
        return(result)

class kayitli_olmayan_ziyaretcileri_goster():
    def __init__(self,kayitli_ziyaretci_olmayan_veritabani):
        self.kayitli_ziyaretci_olmayan_veritabani = kayitli_ziyaretci_olmayan_veritabani
        self.createTable()

    def createTable(self):
        a = veritabani_kayitli_olmayan_ziyaretciler(self.kayitli_ziyaretci_olmayan_veritabani)
        results = a.sorguyu_gerceklestir("select * from tbl_kayitli_olmayan_ziyaretciler",1)
        self.rows = []
        for result in results:
            self.rows.append(result)
        a.conn.close()
        return self.rows
#
