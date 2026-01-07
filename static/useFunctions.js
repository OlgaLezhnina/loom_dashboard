up.compiler('#records, #data, #methods, #overview', function(element, data, meta) {
  checkButtons();
  assignColours();
})

function checkButtons() {
  var counter = 1;
  while (true) {
    var button = document.getElementById("field_name_" + counter);
    if (!button) break;
    selectField(counter);
    counter++; 
  }
} 


// checkbox with id field_name_{id} is responsible for toggling multiple elements
function selectField(index) {
  var button = document.getElementById("field_name_" + index);
  if (!button) return undefined;
  const prefixes = ["pp_", "st_", "au_", "py_", "r_", "csv_", "fin_",
                    "dp_", "ds_", "ae_", "ma_", "ca_", "gc_", "ra_", "cp_", "cd_", "fa_"];
  for (const prefix of prefixes) {
      var x = document.getElementById(prefix + index);
      if (!x) continue;
      if (button.checked) {
        x.style.display = "block";
      } else {
        x.style.display = "none";
      }
  }
} 

function selectColour(index) {
  var x = document.getElementsByClassName('colour_' + index);
  const colours = ["#9FD0F0","#F0B49F", "#CFA6F0", "#A0E0B0", "#F0D39F", 
                   "#B0B4F0", "#F0A0C6", "#9FC6A0", "#C6D0F0", "#A0C0E0"]; 
  for (let element of x) {
    element.style.background = colours[(index-1)%colours.length];
  }
}

function assignColours() {
  var counter = 1;
  while (true) {
    var button = document.getElementById("field_name_" + counter);
    if (!button) break;
    selectColour(counter);
    counter++; 
  }
  var index = counter - 1;
  var x = document.getElementsByClassName('colour_' + index);
  for (let element of x) {
    element.style.background = "#B0B0B8";
  }
} 

