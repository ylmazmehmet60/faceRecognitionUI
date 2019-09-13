eel.tum_kamera_goster()(function(list){
  var i;
  var options = '';
  for (i = 0; i < list.length; i++)
    options += '<option value="'+list[i][4]+'"></option>';
  document.getElementById('kamera_listesi').innerHTML = options;
})

async function kamerayi_listboxa_ekle(m1) {
  var m1 = document.getElementById(m1).value;
  if (m1 != ""){
    eel.kamerayi_listboxa_ekle(m1)(function(list){
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
      eel.py_kamera_listesi_sil(text);
  }
}

eel.tum_calisan_goster()(function(list){
  var table = document.getElementById("add_new_row");
  var cell;
  for (i = 0; i < list.length; i++){
    var row = table.insertRow(i);
      for (j = 0; j < list[i].length; j++){
        if (j==0){
          cell = row.insertCell(j);
          cell.innerHTML = '<input type="radio" name="calisanlar" value="'+list[i][j]+'"/>';
        }else{
          cell = row.insertCell(j);
          cell.innerHTML = list[i][j];
        }
      }
  }

  $("#yeni_calisan_ekle").click(function() {
    var ad = $('#ad').val();
    var soyad = $('#soyad').val();
    var birim = $('#birim').val();
    eel.py_calisan_ekle(ad, soyad, birim);
    location.reload();
  })
  var row_number;
  var guncelle_id;
  $( "input[name='calisanlar']").click(function() {
    var k = document.querySelector('input[name="calisanlar"]:checked').value;
    row_number = $(this).closest("tr")[0].rowIndex;
    eel.calisan_ara(k)(function(list){
      guncelle_id=list[0][0];
      document.getElementById("ad").value = list[0][1];
      document.getElementById("soyad").value = list[0][2];
      document.getElementById("birim").value = list[0][3];
    })
  })

  $( "#secilmis_bul" ).click(function() {
    var k = document.querySelector('input[name="calisanlar"]:checked').value;
    document.getElementById("add_new_row").deleteRow(row_number-1);
    eel.calisan_sil(k);
  })

  $( "#calisan_guncelle" ).click(function() {
    var ad = $('#ad').val();
    var soyad = $('#soyad').val();
    var birim = $('#birim').val();
    eel.calisan_guncelle(guncelle_id,ad, soyad, birim,);
    location.reload();
  })
})
