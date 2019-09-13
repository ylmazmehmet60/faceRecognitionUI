$("#cam_list").prop('disabled', true);
$("#kayit").prop('disabled', true);
document.getElementById('loading').style.display = 'none';

eel.tum_calisan_goster()(function(list){
  var i;
  var options = '';
  for (i = 0; i < list.length; i++)
    options += '<option value="'+list[i][0]+','+list[i][1]+' '+list[i][2]+'"></option>';
  document.getElementById('kisi_listesi').innerHTML = options;
})
eel.tum_kamera_goster()(function(list){
  var i;
  var options = '';
  for (i = 0; i < list.length; i++)
    options += '<option value="'+list[i][4]+'"></option>';
  document.getElementById('kamera_listesi').innerHTML = options;
})

var kamera_turu=null
$( document ).ready(function() {
  $( "input[name='kamera-turu']").click(function() {
    kamera_turu = $('input[name="kamera-turu"]:checked').val();
    if (kamera_turu == 1) {
      $("#cam_list").prop('disabled', false);
    }
    if (kamera_turu == 2) {
      $("#cam_list").prop('disabled', true);
    }
  })
})

$( "#baglan").click(async function() {
  switch (kamera_turu) {
    case '1':
      var cam = $('#cam_list').val();
      if (cam) {
        document.getElementById('loading').style.display = 'block';
        var goruntu = await eel.kayitli_kameralardan_anlik_goruntu_al(cam)();
        if(goruntu[0]=='rtsp'){
          document.getElementById('loading').style.display = 'none';
          $('#img_kamera_goruntusu').attr('src', 'http://localhost:8886/'+goruntu[1]+"?time=" + new Date());
        }else{
          $.get(goruntu).done(function () {
             document.getElementById('loading').style.display = 'none';
             $('#img_kamera_goruntusu').attr('src', goruntu+"?time=" + new Date());
          }).fail(function () {
             document.getElementById('loading').style.display = 'none';
             $('#img_kamera_goruntusu').attr('src', "img/default-error.png");
          })
        }
      }else{
        toastr.error("Kamera Seçmediniz","Dikkat");
      }
      break;
    case '2':
        document.getElementById('loading').style.display = 'block';
        var goruntu = await eel.pc_kamerasindan_anlik_goruntu_al()();
        document.getElementById('loading').style.display = 'none';
        $('#img_kamera_goruntusu').attr('src', 'http://localhost:8886/'+goruntu+"?time=" + new Date());
      break;
  }
})

async function getImage(get) {
  var resim_ismi = $('#tc').val();
  var kime_geldi = $('#kime_geldi').val();
  var cam = $('#cam_list').val();
  var res = kime_geldi.split(",");
  if (res.length==2){
    kime_geldi=res[0];
    resim_ismi+='_'+kime_geldi;
  }
  eel.checkFolderExist()().then(function(result) {
    if (result == false) {
      toastr.error("Kayıt Yeri Seçmediniz","Dikkat");
    }else{
      switch (kamera_turu) {
        case '1':
          eel.kayitli_kameradan_resim_cekme(resim_ismi,cam)(function(list){
          var cikisyap = list[0];
            if (cikisyap == true) {
              $("#kayit").prop('disabled', true);
              toastr.warning('Çıkış yaptığınız için kaydedilmedi',"Hmm");
            }else{
              toastr.success(resim_ismi+' Resmi başarıyla kaydedildi',"Bravo");
              $("#kayit").prop('disabled', false);
            }
          })
        break;
        case '2':
          eel.pc_kamerasindan_resim_cek(resim_ismi)(function(list){
          var gelen_isim = list[0];
          var cikisyap = list[1];
            if (cikisyap == true) {
              $("#kayit").prop('disabled', true);
              toastr.warning('Çıkış yaptığınız için kaydedilmedi',"Hmm");
            }else{
              toastr.success(gelen_isim+' Resmi başarıyla kaydedildi',"Bravo");
              $("#kayit").prop('disabled', false);
            }
          })
        break;
      }
    }
  })
}

$( "#kayit").click(function() {
  var tc = $('#tc').val();
  var adi = $('#adi').val();
  var soyadi = $('#soyadi').val();
  var telefon = $('#telefon').val();
  var adres = $('#adres').val();
  var kime_geldi = $('#kime_geldi').val();
  var res = kime_geldi.split(",");
  if (res.length==2){
    kime_geldi=res[0];
  }
  eel.ziyaretci_ekle(tc, adi, soyadi, telefon, adres, kime_geldi);
  toastr.success('Kayıt başarıyla eklendi. Yönlendiriliyorsunuz.',"Bravo");
  window.setTimeout(function(){
    window.location.reload()
  }, 3000);
})
