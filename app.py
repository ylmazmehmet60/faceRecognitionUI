import eel
import time
from tkinter import filedialog
from tkinter import *
import package
import os

def on_close(page, sockets):
    print(page, 'sayfası kapatıldı.')

web_options = {
    'mode': "chrome-app",
    'host': 'localhost',
    'port': 8886,
	#'chromeFlags': ["--start-fullscreen"],
}

eel.init('web')

class kamera_takip_arayuz():
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	veritabani_kayitli_ziyaretci = "kayitli_ziyaretci_.db"
	veritabani_kayitli_olmayan_ziyaretci = "kayitli_olmayan_ziyaretci_.db"
	veritabani_ismi="takip_.db"
	kamera_veritabani="kameralar_.db"
	calisan_veritabani="calisan_.db"
	ziyaretci_veritabani="ziyaretci_.db"
	anlik_goruntu_resim_yolu=BASE_DIR+"\ ".strip()+"web"+"\ ".strip()+"img"
	resimyolu=BASE_DIR+"\ ".strip()+"resimler"
	ip_adresleri = []
	asil_ip_adresi_linkleri = []#bunu sil
	tumlesik_ip_adresi_linkleri=[]
	tumlesik_ip_adresi_linkleri_allias=[]
	kullanici_adi = ""
	kullanici_sifre = ""

	@eel.expose
	def btn_RaporClick(aranan):
		a = package.rapor_datagrid_view(kamera_takip_arayuz.veritabani_ismi, aranan)
		return a.rows

    #------------------------------KAMERA SAYFASI-----------------------------#
	@eel.expose
	def kamera_ekle(kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti):
		kamera_ekle = package.yeni_kamera_ekle(kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti ,kamera_takip_arayuz.kamera_veritabani)
		a = package.tum_kameralari_ver(kamera_takip_arayuz.kamera_veritabani)
		return a.rows

	@eel.expose
	def kamera_sil(id):
		kamera_sil = package.mevcut_kamera_sil(id,kamera_takip_arayuz.kamera_veritabani)

	@eel.expose
	def tum_kamera_goster():
		a = package.tum_kameralari_ver(kamera_takip_arayuz.kamera_veritabani)
		return a.rows

	@eel.expose
	def kamera_ara(aranan):
		a = package.kamera_ara(aranan,kamera_takip_arayuz.kamera_veritabani)
		return a.rows

	@eel.expose
	def kamera_guncelle(guncelle_id,kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti):
		a = package.kamera_guncelle(guncelle_id,kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti,kamera_takip_arayuz.kamera_veritabani)



    #------------------------------CALISAN SAYFASI-----------------------------#
	kamerayi_listboxa_ekle_array=[]
	@eel.expose
	def kamerayi_listboxa_ekle(kamera):
		kamera_takip_arayuz.kamerayi_listboxa_ekle_array.append(kamera)
		r=kamera
		return r

	@eel.expose
	def py_kamera_listesi_sil(get):
		index=kamera_takip_arayuz.kamerayi_listboxa_ekle_array.index(get)
		del kamera_takip_arayuz.kamerayi_listboxa_ekle_array[index]

	@eel.expose
	def py_calisan_ekle(ad, soyad, birim):
		kamera_list = ','.join(kamera_takip_arayuz.kamerayi_listboxa_ekle_array)
		calisan_ekle = package.yeni_calisan_ekle(ad, soyad, birim,kamera_list, kamera_takip_arayuz.calisan_veritabani)
		kamera_takip_arayuz.kamerayi_listboxa_ekle_array=[]

	@eel.expose
	def tum_calisan_goster():
		a = package.tum_calisanlari_ver(kamera_takip_arayuz.calisan_veritabani)
		return a.rows

	@eel.expose
	def calisan_sil(id):
		calisan_sil = package.mevcut_calisan_sil(id,kamera_takip_arayuz.calisan_veritabani)

	@eel.expose
	def calisan_ara(aranan):
		a = package.calisan_ara(aranan,kamera_takip_arayuz.calisan_veritabani)
		return a.rows

	@eel.expose
	def calisan_guncelle(guncelle_id,ad, soyad, birim):
		guncel_kamera_list = ','.join(kamera_takip_arayuz.kamerayi_listboxa_ekle_array)
		a = package.calisan_guncelle(guncelle_id,ad, soyad, birim, guncel_kamera_list, kamera_takip_arayuz.calisan_veritabani)
		kamera_takip_arayuz.kamerayi_listboxa_ekle_array=[]



    #------------------------------RESIM YOLU-----------------------------#
	@eel.expose
	def btn_ResimyoluClick():
		root = Tk()
		root.withdraw()
		root.wm_attributes('-topmost', 1)
		folder = filedialog.askdirectory()
		kamera_takip_arayuz.resimyolu = folder
		return folder

	@eel.expose
	def checkFolderExist():
		return kamera_takip_arayuz.resimyolu



    #------------------------------ANLIK GORUNTU ALMA-----------------------------#
	@eel.expose
	def pc_kamerasindan_anlik_goruntu_al():
		a = package.pc_kamerasindan_anlik_goruntu_al(kamera_takip_arayuz.anlik_goruntu_resim_yolu)
		return "img/"+a.goruntu+".jpg"

	@eel.expose
	def kayitli_kameralardan_anlik_goruntu_al(hangi_kameradan_goruntu_alinacak):
		kamera_takip_arayuz.ip_adresleri_olustur()
		index=kamera_takip_arayuz.tumlesik_ip_adresi_linkleri_allias.index(hangi_kameradan_goruntu_alinacak)
		goruntu_alinacak_kamera=kamera_takip_arayuz.tumlesik_ip_adresi_linkleri[index]
		print(goruntu_alinacak_kamera)
		print(kamera_takip_arayuz.anlik_goruntu_resim_yolu)
		if("rtsp" in goruntu_alinacak_kamera):
			a = package.rtsp_kamerasindan_anlik_goruntu_al(kamera_takip_arayuz.anlik_goruntu_resim_yolu,goruntu_alinacak_kamera)
			return ['rtsp',"img/"+a.goruntu+".jpg"]
		else:
			return goruntu_alinacak_kamera

	@eel.expose
	def ip_adresleri_olustur():
		a = package.tum_kameralari_ver(kamera_takip_arayuz.kamera_veritabani)
		kamera_takip_arayuz.tumlesik_ip_adresi_linkleri=[]
		kamera_takip_arayuz.tumlesik_ip_adresi_linkleri_allias=[]
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
			kamera_takip_arayuz.tumlesik_ip_adresi_linkleri.append(tekil_ip_adresi)
			kamera_takip_arayuz.tumlesik_ip_adresi_linkleri_allias.append(allias)



    #------------------------------RESIM CEKME-----------------------------#
	@eel.expose
	def pc_kamerasindan_resim_cek(resimismi):
		cikisyap=False
		resimyolu=kamera_takip_arayuz.resimyolu
		b = package.pc_kamerasindan_resim_cek(resimyolu, resimismi, cikisyap)
		b.btn_ResimCekAcilClick()
		return [resimismi, b.cikisyap]

	@eel.expose
	def kayitli_kameradan_resim_cekme(resim_ismi,cam):
		resimyolu=kamera_takip_arayuz.resimyolu
		kamera_takip_arayuz.ip_adresleri_olustur()
		index=kamera_takip_arayuz.tumlesik_ip_adresi_linkleri_allias.index(cam)
		ip=kamera_takip_arayuz.tumlesik_ip_adresi_linkleri[index]
		b = package.kayitli_kameradan_resim_cekme(resimyolu, resim_ismi ,ip)
		b.btn_ResimCekAcilClick()
		return [b.cikisyap]



    #------------------------------ZIYARETCI-----------------------------#
	@eel.expose
	def ziyaretci_ekle(tc, adi, soyadi, telefon, adres, kime_geldi):
		ziyaretci_ekle = package.yeni_ziyaretci_ekle(tc, adi, soyadi, telefon, adres, kime_geldi, kamera_takip_arayuz.ziyaretci_veritabani)

	@eel.expose
	def tum_ziyaretcileri_goster():
		a = package.tum_ziyaretcileri_goster(kamera_takip_arayuz.ziyaretci_veritabani)
		return a.rows


    #------------------------------IZLEME SAYFASI-----------------------------#
	izleme_kamerasini_listboxa_ekle_array=[]
	@eel.expose
	def izleme_kamerasini_listboxa_ekle(kamera):
		kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array.append(kamera)
		return kamera

	@eel.expose
	def izleme_kamera_listesi_listboxdan_sil(get):
		index=kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array.index(get)
		del kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array[index]

	@eel.expose
	def tum_izleme_kamera_listesi_listboxda_goster():
		return kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array

	@eel.expose
	def izleme_ekrani_icin_kameralardan_anlik_goruntu_al():
		rtsp_resim_yolu=kamera_takip_arayuz.BASE_DIR+"\ ".strip()+"web"+"\ ".strip()+"img"+"\ ".strip()+"rtsp_cam_istek"
		gelen_goruntuler=[]
		kamera_takip_arayuz.ip_adresleri_olustur()
		hangi_kameralardan_goruntu_alinacak=kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array
		for kamera in hangi_kameralardan_goruntu_alinacak:
			index=kamera_takip_arayuz.tumlesik_ip_adresi_linkleri_allias.index(kamera)
			tekil_kamera=kamera_takip_arayuz.tumlesik_ip_adresi_linkleri[index]
			a = package.izleme_ekrani_icin_kameralardan_anlik_goruntu_al(rtsp_resim_yolu,tekil_kamera,kamera)
			gelen_goruntuler.append(a.goruntu)
		return gelen_goruntuler

	@eel.expose
	def izleme_ekrani_icin_izlemeyi_baslat():
		if(kamera_takip_arayuz.resimyolu==False or not(kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array)):
			print(kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array)
			return False
		else:
			kamera_takip_arayuz.asil_ip_adresi_linkleri=[]
			kamera_takip_arayuz.ip_adresleri_olustur()
			hangi_kameralardan_goruntu_alinacak=kamera_takip_arayuz.izleme_kamerasini_listboxa_ekle_array
			for kamera in hangi_kameralardan_goruntu_alinacak:
				index=kamera_takip_arayuz.tumlesik_ip_adresi_linkleri_allias.index(kamera)
				kamera_takip_arayuz.asil_ip_adresi_linkleri.append(kamera_takip_arayuz.tumlesik_ip_adresi_linkleri[index])
			print("Adress: ",kamera_takip_arayuz.asil_ip_adresi_linkleri)
			kamera = package.kamera_baslat(kamera_takip_arayuz.resimyolu,kamera_takip_arayuz.asil_ip_adresi_linkleri,kamera_takip_arayuz.veritabani_ismi)

    #------------------------------KAYITLI ve KAYITLI OLMAYAN ZIYARETCI RAPOR-----------------------------#
	@eel.expose
	def kayitli_ziyaretcileri_goster():
		a = package.kayitli_ziyaretcileri_goster(kamera_takip_arayuz.veritabani_kayitli_ziyaretci)
		return a.rows

	@eel.expose
	def kayitli_olmayan_ziyaretcileri_goster():
		a = package.kayitli_olmayan_ziyaretcileri_goster(kamera_takip_arayuz.veritabani_kayitli_olmayan_ziyaretci)
		return a.rows

	@eel.expose
	def kayitli_ziyaretci_tablosu():
		kayitli_ziyaretci = package.kayitli_ziyaretcileri_goster(kamera_takip_arayuz.veritabani_kayitli_ziyaretci)
		kayitli_ziyaretci=kayitli_ziyaretci.rows
		dis=[]
		for i in kayitli_ziyaretci:
			ic=[]
			tc=i[1].split("_")[0]
			ic.append(tc)
			tum_ziyaretci = package.tum_ziyaretcileri_goster(kamera_takip_arayuz.ziyaretci_veritabani)
			for k in tum_ziyaretci.rows:
				if tc in k[1]:
					if (k[2] and k[3] != ''):
						ziyaretci_ad_soyad=k[2]+" "+k[3]
						ic.append(ziyaretci_ad_soyad)
					else:
						ic.append('isim girilmemis')
			kamera=i[2]
			ic.append(kamera)
			calisan_id=i[1].split("_")[1]
			calisan=package.calisan_ara(calisan_id,kamera_takip_arayuz.calisan_veritabani)
			kime_geldi_adi_soyadi_birim=calisan.rows[0][1]+" "+calisan.rows[0][2]
			ic.append(kime_geldi_adi_soyadi_birim)
			tarih=i[3]
			ic.append(tarih)
			dis.append(ic)
		return dis

	@eel.expose
	def kayitli_olmayan_ziyaretci_tablosu():
		kayitli_olmayan_ziyaretci = package.kayitli_olmayan_ziyaretcileri_goster(kamera_takip_arayuz.veritabani_kayitli_olmayan_ziyaretci)
		kayitli_olmayan_ziyaretci=kayitli_olmayan_ziyaretci.rows
		dis=[]
		for i in kayitli_olmayan_ziyaretci:
			ic=[]
			tc=i[1].split("_")[0]
			ic.append(tc)
			tum_ziyaretci = package.tum_ziyaretcileri_goster(kamera_takip_arayuz.ziyaretci_veritabani)
			for k in tum_ziyaretci.rows:
				if tc in k[1]:
					if (k[2] and k[3] != ''):
						ziyaretci_ad_soyad=k[2]+" "+k[3]
						ic.append(ziyaretci_ad_soyad)
					else:
						ic.append('isim girilmemis')
			kamera=i[2]
			ic.append(kamera)
			calisan_id=i[1].split("_")[1]
			calisan=package.calisan_ara(calisan_id,kamera_takip_arayuz.calisan_veritabani)
			kime_geldi_adi_soyadi_birim=calisan.rows[0][1]+" "+calisan.rows[0][2]
			ic.append(kime_geldi_adi_soyadi_birim)
			tarih=i[3]
			ic.append(tarih)
			dis.append(ic)
		return dis


	@eel.expose
	def RunPyPy():
		y=kamera_takip_arayuz.BASE_DIR+"\ ".strip()+"pypy"+"\ ".strip()+"pypy.exe"
		x=os.startfile(y)
		return x

	@eel.expose
	def StopPyPy():
		x=os.system("taskkill /f /im pypy.exe")
		return x

	@eel.expose
	def exe_calisiyormu():
		from win32com.client import GetObject
		WMI = GetObject('winmgmts:')
		if len(WMI.ExecQuery('select * from Win32_Process where Name like "%s%s"' % ("pypy",'%'))) > 0:
			return True
		else:
			return False


eel.start('main_page.html', options=web_options, callback=on_close, size=(1366, 768))

while True:
	eel.sleep(4)
