up.compiler('#records, #data, #methods', function(element, data, meta) {
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
  const prefixes = ["pp_", "st_", "au_", "py_", "r_", "csv_", 
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
  const colours = ["#C5D89D","#FFF2C6", "#9CAB84", "#FDDB3A", "#F8FAB4", 
                   "#FFD6BA", "#F4BBBB", "#B6FFA1", "#ADC4CE", "#D8D3CD"]; 
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
} 
