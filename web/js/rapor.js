eel.kayitli_ziyaretci_tablosu()(function(list){
  var table = document.getElementById("add_new_row");
  var cell;
  for (i = 0; i < list.length; i++){
    var row = table.insertRow(i);
      for (j = 0; j < list[i].length; j++){
        cell = row.insertCell(j);
        cell.innerHTML = list[i][j];
      }
  }
})

eel.kayitli_olmayan_ziyaretci_tablosu()(function(list){
  var table = document.getElementById("add_new_row_iki");
  var cell;
  for (i = 0; i < list.length; i++){
    var row = table.insertRow(i);
      for (j = 0; j < list[i].length; j++){
        cell = row.insertCell(j);
        cell.innerHTML = list[i][j];
      }
  }
})
