/**
 * Check the states of all buttons, show/hide elements, and re-colour domain-related entries 
   when unpoly adds a fragment with one of these ids
 */
up.compiler('#records, #data, #methods, #overview', function(element, data, meta) {
  checkButtons();
  assignColours();
})


/**
 * Show/ hide all related elements depenging on the field_button state
 */
function checkButtons() {
  var counter = 1;
  while (true) {
    var button = document.getElementById("field_name_" + counter);
    if (!button) break;
    selectField(counter);
    counter++; 
  }
}

/**
 * Show/ hide all related elements when a field(research domain) is selected/deselected
 * @param  {Number} index The index of the field_button
 */
function selectField(index) {
  // this checkbox is responsible for toggling multiple elements
  var button = document.getElementById("field_name_" + index);
  if (!button) return undefined;
  // these prefixes are in ids of elements to be displayed/hidden
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

/**
 * Set a colour for elements of the colour_{index} class
 * @param  {Number} index The index for the colours
 */
function selectColour(index) {
  var x = document.getElementsByClassName('colour_' + index);
  const colours = ["#9FD0F0","#F0B49F", "#CFA6F0", "#A0E0B0", "#F0D39F", 
                   "#B0B4F0", "#F0A0C6", "#9FC6A0", "#C6D0F0", "#A0C0E0",
                   "#BBDEF4", "#F4CABB", "#DDC0F4", "#BCE9C7", "#F4E0BB",
                    "#C7CAF4", "#F4BCD7", "#BBD7BC", "#D7DEF4", "#BCD2E9"]; 
  for (let element of x) {
    element.style.background = colours[(index-1)%colours.length];
  }
}


/**
 * Assign a colour to each field_button and all related elements
 */
function assignColours() {
  var counter = 1;
  while (true) {
    var button = document.getElementById("field_name_" + counter);
    if (!button) break;
    selectColour(counter);
    counter++; 
  }
  // hardcode the grey colour for 'Overall', which is the last field_button
  var index = counter - 1;
  var x = document.getElementsByClassName('colour_' + index);
  for (let element of x) {
    element.style.background = "#B0B0B8";
  }
} 

