eel.tum_kamera_goster()(function(list){
  var table = document.getElementById("add_new_row");
  var cell;
  for (i = 0; i < list.length; i++){
    var row = table.insertRow(i);
      for (j = 0; j < list[i].length; j++){
        if (j==0){
          cell = row.insertCell(j);
          cell.innerHTML = '<input type="radio" name="kameralar" value="'+list[i][j]+'"/>';
        }else{
          cell = row.insertCell(j);
          cell.innerHTML = list[i][j];
        }
      }
  }
  $( "#yeni_ekle").click(function() {
    var kullanici_adi = $('#kullanici_adi').val();
    var parola = $('#parola').val();
    var ip_numarasi = $('#ip_numarasi').val();
    var allias = $('#allias').val();
    var protokol = $('#protokol').val();
    var uzanti = $('#uzanti').val();
    eel.kamera_ekle(kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti);
    location.reload();
  })
  var row_number;
  var guncelle_id;
  $( "input[name='kameralar']").click(function() {
    var k = document.querySelector('input[name="kameralar"]:checked').value;
    row_number = $(this).closest("tr")[0].rowIndex;
    eel.kamera_ara(k)(function(list){
      guncelle_id=list[0][0];
      document.getElementById("kullanici_adi").value = list[0][1];
      document.getElementById("parola").value = list[0][2];
      document.getElementById("ip_numarasi").value = list[0][3];
      document.getElementById("allias").value = list[0][4];
      document.getElementById("protokol").value = list[0][5];
      document.getElementById("uzanti").value = list[0][6];
    })
  })
  $( "#secilmis_bul" ).click(function() {
    var k = document.querySelector('input[name="kameralar"]:checked').value;
    document.getElementById("add_new_row").deleteRow(row_number-1);
    eel.kamera_sil(k);
  })
  $( "#kamera_guncelle" ).click(function() {
    var kullanici_adi = $('#kullanici_adi').val();
    var parola = $('#parola').val();
    var ip_numarasi = $('#ip_numarasi').val();
    var allias = $('#allias').val();
    var protokol = $('#protokol').val();
    var uzanti = $('#uzanti').val();
    eel.kamera_guncelle(guncelle_id,kullanici_adi, parola, ip_numarasi, allias, protokol, uzanti);
    location.reload();
  })
})
