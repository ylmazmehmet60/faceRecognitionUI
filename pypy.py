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
from multiprocessing import Pool,freeze_support
import random


class calisan_veritabani():
    def __init__(self,calisan_veritabani):
        self.calisan_veritabani=calisan_veritabani

    def sorguyu_gerceklestir(self,sorgu,type=0):
        self.conn = sqlite3.connect(self.calisan_veritabani)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)
        self.conn.commit()
        self.conn.close()
        return(result)

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

class belirli_calisanlari_ver():
    def __init__(self,calisan_veritabani,aranan):
        self.calisan_veritabani = calisan_veritabani
        self.aranan = aranan
        self.sorgu()

    def sorgu(self):
        a = calisan_veritabani(self.calisan_veritabani)
        self.result = a.sorguyu_gerceklestir("select * from tbl_calisan where id='{}'".format(self.aranan),1)
        a.conn.close()
        return self.result


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

class veritabani_kayitli_ziyaretciler():
    def __init__(self,veritabani_ismi):
        self.veritabani_ismi=veritabani_ismi
        self.tabloyu_olustur()

    def butun_sonuclari_ver(self):
        sonuc = self.sorguyu_gerceklestir("select * from tbl_kayitli_ziyaretciler",1)
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
            self.sorguyu_gerceklestir("INSERT INTO tbl_kayitli_ziyaretciler(isim,kamera_ismi,tarih,ilk_goruntulenme,kac_kare_goruntulenme) "+
                                      "VALUES ('{}','{}','{}',{},{})"
                                      .format(dizi[0],kamera_ismi,tarih,dizi[1],dizi[2]))
        else:
            self.sorguyu_gerceklestir("UPDATE tbl_kayitli_ziyaretciler SET kac_kare_goruntulenme='{}' WHERE id={}".format(dizi[2]+kackezgoruntelenmis,tbl_takip_id))

    def kullanicinin_kackarede_oldugunu_ver(self,isim,kamera_ismi,tarih):
        kackezgoruntelenmis = 0
        sorgu ="select * from tbl_kayitli_ziyaretciler where isim='{}' and kamera_ismi='{}' and tarih='{}'".format(isim,kamera_ismi,tarih)
        sonuc = self.sorguyu_gerceklestir(sorgu,1)
        for i in sonuc:
            kackezgoruntelenmis = int(i[5])
        return(kackezgoruntelenmis)

    def isimli_kisi_sistemde_mevcut_mu(self,isim,kamera_ismi, tarih):#bir kişinin sistemde olup olmadığını buluyor
        kackezgoruntelenmis = 0
        sorgu ="select * from tbl_kayitli_ziyaretciler where isim='{}' and kamera_ismi='{}' and tarih='{}'".format(isim,kamera_ismi,tarih)
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
                                      "tbl_kayitli_ziyaretciler("+
                                          "id INTEGER PRIMARY KEY autoincrement,"+
                                          "isim varchar(100),"+
                                          "kamera_ismi varchar(100),"+
                                          "tarih varchar(100),"+
                                          "ilk_goruntulenme int(6),"+
                                          "kac_kare_goruntulenme int(6)"+
                                      ")")

class veritabani_kayitli_olmayan_ziyaretciler():
    def __init__(self,veritabani_ismi):
        self.veritabani_ismi=veritabani_ismi
        self.tabloyu_olustur()

    def butun_sonuclari_ver(self):
        sonuc = self.sorguyu_gerceklestir("select * from tbl_kayitli_olmayan_ziyaretciler",1)
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
            self.sorguyu_gerceklestir("INSERT INTO tbl_kayitli_olmayan_ziyaretciler(isim,kamera_ismi,tarih,ilk_goruntulenme,kac_kare_goruntulenme) "+
                                      "VALUES ('{}','{}','{}',{},{})"
                                      .format(dizi[0],kamera_ismi,tarih,dizi[1],dizi[2]))
        else:
            self.sorguyu_gerceklestir("UPDATE tbl_kayitli_olmayan_ziyaretciler SET kac_kare_goruntulenme='{}' WHERE id={}".format(dizi[2]+kackezgoruntelenmis,tbl_takip_id))

    def kullanicinin_kackarede_oldugunu_ver(self,isim,kamera_ismi,tarih):
        kackezgoruntelenmis = 0
        sorgu ="select * from tbl_kayitli_olmayan_ziyaretciler where isim='{}' and kamera_ismi='{}' and tarih='{}'".format(isim,kamera_ismi,tarih)
        sonuc = self.sorguyu_gerceklestir(sorgu,1)
        for i in sonuc:
            kackezgoruntelenmis = int(i[5])
        return(kackezgoruntelenmis)

    def isimli_kisi_sistemde_mevcut_mu(self,isim,kamera_ismi, tarih):#bir kişinin sistemde olup olmadığını buluyor
        kackezgoruntelenmis = 0
        sorgu ="select * from tbl_kayitli_olmayan_ziyaretciler where isim='{}' and kamera_ismi='{}' and tarih='{}'".format(isim,kamera_ismi,tarih)
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
                                      "tbl_kayitli_olmayan_ziyaretciler("+
                                          "id INTEGER PRIMARY KEY autoincrement,"+
                                          "isim varchar(100),"+
                                          "kamera_ismi varchar(100),"+
                                          "tarih varchar(100),"+
                                          "ilk_goruntulenme int(6),"+
                                          "kac_kare_goruntulenme int(6)"+
                                      ")")


class kamera_baslat():
    resimyolu = os.path.dirname(os.path.abspath(__file__))+"\ ".strip()+"resimler"
    #ip_adresleri = ip_adresleri
    baslangic_zaman = "18:00"
    calisan_veritabani = "calisan_.db"
    veritabani_kayitli_ziyaretci = "kayitli_ziyaretci_.db"
    veritabani_kayitli_olmayan_ziyaretci = "kayitli_olmayan_ziyaretci_.db"
    istenilen_kare_sayisinda_kabul = 5
    kacinci_saniyede_veritabani_guncellensin = 5
    bulunan_isimler = []
    resim_yolundaki_yuzler=[]
    calisan_listesi=[]
    faceCascade = cv2.CascadeClassifier('web/data/xml/haarcascade_frontalface_alt.xml')

    def calisan_listesi():
        calisan_listesi = tum_calisanlari_ver(kamera_baslat.calisan_veritabani)
        return calisan_listesi.rows

    def veritabani_kayitli_ziyaretciler_guncelle(veritabani_kayitli_ziyaretci,bilgi,kamera_ismi,tarih):
        a = veritabani_kayitli_ziyaretciler(veritabani_kayitli_ziyaretci)
        a.butun_bulunan_yuzleri_kontrollu_ekle(bilgi,kamera_ismi,tarih)

    def veritabani_kayitli_olmayan_ziyaretciler_guncelle(veritabani_kayitli_olmayan_ziyaretci,bilgi,kamera_ismi,tarih):
        a = veritabani_kayitli_olmayan_ziyaretciler(veritabani_kayitli_olmayan_ziyaretci)
        a.butun_bulunan_yuzleri_kontrollu_ekle(bilgi,kamera_ismi,tarih)

    def isim_kayitli_mi(bulunan_isim):
        kayitli_mi=False
        i=0
        for isim in kamera_baslat.bulunan_isimler:
            if(isim[0] == bulunan_isim):
                kayitli_mi=True
                kamera_baslat.bulunan_isimler[i][2]+=1#kisinin istenilen kare sayisi kadar bulundugunda doğruluğunun kabulu
                break
            i+=1
        return(kayitli_mi)

    def frame_duzenle(frame_old,frame_sayisi):
        frame = cv2.resize(frame_old, (0, 0), fx=0.80, fy=0.80)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        bulunan_yuzler = kamera_baslat.faceCascade.detectMultiScale(gray, 1.3, 5)
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
                for siradaki_yuz in kamera_baslat.resim_yolundaki_yuzler:
                    face_object = face_recognition.compare_faces([kamera_baslat.resim_yolundaki_yuzler[siradaki_yuz]], bulunacak_face[0])
                    if(face_object[0]):
                        bulunan_isim=siradaki_yuz.split('.')[0]
                        if(kamera_baslat.isim_kayitli_mi(bulunan_isim)!=True):
                            kamera_baslat.bulunan_isimler.append([bulunan_isim,int(frame_sayisi/30),1])
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

    def goruntuleri_izle(ip_adresleri):
        kisi_dogru_kamerada_mi=False
        _calisan_listesi=kamera_baslat.calisan_listesi()
        allias=ip_adresleri.split('%&_____&%')[1]

        resimler = os.listdir(kamera_baslat.resimyolu)
        yuzler = {}
        for resim in resimler:
            tur = resim.split('.')[1]
            if(tur == "jpg" or tur == "jpeg"):
                if(face_recognition.face_encodings(face_recognition.load_image_file(kamera_baslat.resimyolu+"/"+resim))):
                    yuzler[resim]=face_recognition.face_encodings(face_recognition.load_image_file(kamera_baslat.resimyolu+"/"+resim))[0]
        kamera_baslat.resim_yolundaki_yuzler = yuzler

        frame_sayisi=1
        kamera_baslat.bulunan_isimler=[]
        goruntu_yolu=""
        print('Kamera AKTİF')
        print(allias,' isimli ',ip_adresleri.split('%&_____&%')[0],' adresine sahip kamera BAŞLATILDI...')
        while(True):
            cikisyap=False
            ekranlar=2
            ip=ip_adresleri.split('%&_____&%')[0]
            kamera_baslat.bulunan_isimler=[]
            if("@" in ip):
                ip = ip[ip.find("@")+1:]
            goruntu_yolu = ip

            frame = None
            #print('Taranan Kamera: ',ip)
            if("rtsp" in ip):
                cap = cv2.VideoCapture(ip)
                (ret,frame) = cap.read()
            else:
                with urllib.request.urlopen(ip) as url:
                    imgResp = url.read()

                imgNp = np.array(bytearray(imgResp),dtype=np.uint8)
                if(len(imgNp)>0):
                    frame = cv2.imdecode(imgNp,-1)
            if(frame is not None):

                frame = kamera_baslat.frame_duzenle(frame,frame_sayisi)

                (height, width, channels) = frame.shape
                alta_yazdir = 0
                for bulunan in kamera_baslat.bulunan_isimler:
                    rgb_bulunan=(255, 255, 255)
                    if(bulunan[2]>=kamera_baslat.istenilen_kare_sayisinda_kabul):
                        rgb_bulunan=(0, 255, 0)
                    alta_yazdir+=20
                if(kamera_baslat.bulunan_isimler):
                    if(kamera_baslat.bulunan_isimler[0]):
                        _ayir = kamera_baslat.bulunan_isimler[0][0].split('_')[1]
                        for kv in range(len(_calisan_listesi)):
                            if (str(_calisan_listesi[kv][0]) == _ayir):
                                allias_arr=[]
                                allias_arr=_calisan_listesi[kv][4].split(',')
                                if allias in allias_arr:
                                    kisi_dogru_kamerada_mi=True
                                else:
                                    kisi_dogru_kamerada_mi=False
                        if(kisi_dogru_kamerada_mi==True):
                            print('......KİŞİ TESPİT EDİLDİ.... DOĞRU Kamerada... Kamera İsmi: ',allias)
                            kamera_baslat.veritabani_kayitli_ziyaretciler_guncelle(kamera_baslat.veritabani_kayitli_ziyaretci,kamera_baslat.bulunan_isimler,allias,str(datetime.datetime.today().strftime('%d, %m %y')))
                        else:
                            print('......KİŞİ TESPİT EDİLDİ.... YANLIS Kamerada... Kamera İsmi: ',allias)
                            kamera_baslat.veritabani_kayitli_olmayan_ziyaretciler_guncelle(kamera_baslat.veritabani_kayitli_olmayan_ziyaretci,kamera_baslat.bulunan_isimler,allias,str(datetime.datetime.today().strftime('%d, %m %y')))
                        print('Sonuçları Arayüz > Dosya > Rapor Kısmından görebilirsiniz')
                        print('İsterseniz belirli bir kamerayı manuel izlemek için Arayüz > Dosya > İzleme Ekranından listeye istediğiniz kamerayı ekleyip izlemeyi başlatın ')
                        print('Böylelikle senkronize bir sekilde izleme yapabilirsiniz.')
            frame_sayisi+=1

class kamera_veritabani():
    def __init__(self,kamera_veritabani):
        self.kamera_veritabani=kamera_veritabani

    def sorguyu_gerceklestir(self,sorgu,type=0):#her sorgu işleminde dinamik bir yapı
        self.conn = sqlite3.connect(self.kamera_veritabani)
        c = self.conn.cursor()
        result = c.execute(sorgu)
        if(type==1):return(result)#eğer bir yerde sorgu sonucunu yazdırmak istiyor isek, close() demeden önce yapmalıyız, bunu yapmak içinde type i belirtmek yeterli olacaktır
        self.conn.commit()
        self.conn.close()
        return(result)

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

def main():
    kamera_veritabani="kameralar_.db"
    veritabani_ismi="takip_.db"

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    resimyolu=BASE_DIR+"\ ".strip()+"resimler"

    a = tum_kameralari_ver(kamera_veritabani)
    tumlesik_ip_adresi_linkleri=[]
    tumlesik_ip_adresi_linkleri_allias=[]
    tekil_ip_adresi=""
    kamera_veritabani_satirlari=[]
    kamera_veritabani_satirlari = a.rows
    for kamera in kamera_veritabani_satirlari:
    	kullanici_adi = kamera[1]
    	parola = kamera[2]
    	ip_numarasi = kamera[3]
    	allias = kamera[4]
    	protokol = kamera[5]
    	uzanti = kamera[6]
    	tekil_ip_adresi = protokol.strip()
    	if(kullanici_adi!="" and parola!=""):
    		tekil_ip_adresi+= kullanici_adi+":"+parola+"@"
    	tekil_ip_adresi += ip_numarasi
    	if(uzanti!=""):
    		tekil_ip_adresi += uzanti
    	tumlesik_ip_adresi_linkleri.append(tekil_ip_adresi+'%&_____&%'+allias)
    yazi_list=['İzleme Başlatılıyor...', 'İp Listesi Oluşturuluyor...', 'Birkaç Adım Kaldı...', 'İzleme başlayınca taranan ipler gösterilecek...']
    print(random.choice(yazi_list))
    freeze_support()
    p = Pool(len(tumlesik_ip_adresi_linkleri))
    p.map(kamera_baslat.goruntuleri_izle, tumlesik_ip_adresi_linkleri)
    p.close()
    p.join()

if __name__=='__main__':
    main()
