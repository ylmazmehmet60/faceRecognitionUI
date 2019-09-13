document.getElementById('loading_izleme').style.display = 'none';
eel.tum_kamera_goster()(function(list){
  var i;
  var options = '';
  for (i = 0; i < list.length; i++)
    options += '<option value="'+list[i][4]+'"></option>';
  document.getElementById('kamera_listesi').innerHTML = options;
})
eel.tum_izleme_kamera_listesi_listboxda_goster()(function(list){
  var i;
  var options = '';
  for (i = 0; i < list.length; i++)
    options += '<option value="'+list[i]+'">'+list[i]+'</option>';
  document.getElementById('kamera_listesi_yaz').innerHTML = options;
})
async function kamerayi_listboxa_ekle(m1) {
  var m1 = document.getElementById(m1).value;
  if (m1 != ""){
    eel.izleme_kamerasini_listboxa_ekle(m1)(function(list){
        var x = document.getElementById("kamera_listesi_yaz");
        var c = document.createElement("option");
        c.text = list;
        x.options.add(c, 1);
    });
  }else {
    toastr.warning('Lütfen kutuları doldurun !',"Dikkat");
  }
}
function kamera_listesi_sil(){
  var x = document.getElementById("kamera_listesi_yaz");
  var y = document.getElementById("kamera_listesi_yaz").options;
  if (!!y[x.selectedIndex]) {
      var text = y[x.selectedIndex].text;
      x.remove(x.selectedIndex);
      eel.izleme_kamera_listesi_listboxdan_sil(text);
  }
}

$( "#baglan").click(async function() {
    document.getElementById('loading_izleme').style.display = 'block';
    eel.izleme_ekrani_icin_kameralardan_anlik_goruntu_al()(function(list){
      var i;
      var options = '';
      var len = list.length
      for (i = 0; i < len; i++)
        options += `<div class="col-lg-4"style="padding-top:0px;padding-bottom:15px;">
                      <h4 style="margin-bottom: 0px;margin-top: 0px;text-align:center;padding-bottom: 10px;">`+list[i]+`</h4>
                      <img src="http://localhost:8886/img/rtsp_cam_istek/`+list[i]+`.jpg?time=`+  new Date() +` id="img_kamera_goruntusu" class="img-rounded" height="25%">
                    </div> `;

      document.getElementById('izgara_kamera').innerHTML = options;
      document.getElementById('loading_izleme').style.display = 'none';
    })
})

$( "#izleme_baslat").click(async function() {
  eel.izleme_ekrani_icin_izlemeyi_baslat()().then(function(result) {
    if (result == false) {
      toastr.error("Lütfen resim yolu seçiniz ve kamera seçiniz!","Dikkat");
    }else{
      toastr.success("İzleme bitirildi","Dikkat");
    }
  });
})
