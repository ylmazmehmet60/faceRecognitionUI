function RunExe()
{
  $("#degis").show();
  $("#sistemi_baslat_buton").prop('disabled', true);
  $("#sistemi_durdur_buton").prop('disabled', false);
  eel.RunPyPy()(function(list){
    toastr.success("Sistem Arka Planda Başlatılıyor...","Harika!");
  })
}
function StopExe()
{
  $("#degis").hide();
  $("#sistemi_baslat_buton").prop('disabled', false);
  $("#sistemi_durdur_buton").prop('disabled', true);
  eel.StopPyPy()(function(list){
    toastr.warning("Sistem Durduruldu...","Harika!");
  })
}
eel.exe_calisiyormu()(function(list){
    if(list==false){
      $("#degis").hide();
      $("#sistemi_baslat_buton").prop('disabled', false);
      $("#sistemi_durdur_buton").prop('disabled', true);
    }else{
      $("#degis").show();
      $("#sistemi_baslat_buton").prop('disabled', true);
      $("#sistemi_durdur_buton").prop('disabled', false);
    }
})

var i = 0;
function change() {
  var doc = document.getElementById("degisiki");
  var color = ["#178394", "#0c4750"];
  doc.style.backgroundColor = color[i];
  i = (i + 1) % color.length;
}
setInterval(change, 500);
