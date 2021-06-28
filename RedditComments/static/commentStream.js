$('#spinner').hide();

// Create two promises that will race each other.
// 1. promise1 - This promise is only resolved if refresh rate is not "Don't Refresh" ( > 0).
//               It is resolved after the amount of the time the refresh rate is defined for passes.
//               Then we will call ajax to reload the comments in page.
// 2. promise2 - This promise is resolved whenever the refresh rate drop down has changed value.
//                 This means that if the refresh rate is changed while we are waiting for a new refresh, the current
//               refresh wait time is reset.

async function startRace (){
// get current refresh rate if refresh rate < 0 we don't refresh.
let refreshRateSelect = document.getElementById("refresh-rate-options");
let refreshRateInt = refreshRateSelect.options[refreshRateSelect.selectedIndex].value;

let promise1 = new Promise(function(resolve, reject) {
  console.log("in here prm1");
  // only resolve this promise if refresh rate is not set to don't refresh.'
  // resolve after the amount of time defined in the refresh rate drop down.
    if(refreshRateInt > 0)
    {
        setTimeout(resolve, refreshRateInt, '1');
    }
});

// second promise which is resolved whenever the refresh rate drop is changed.
let promise2 = new Promise(function(resolve, reject) {
    $("#refresh-rate-options").change(function(){
    // resolve with -2 as other values have been taken by the refresh rate promise1.
        resolve('-2');
    });
});

Promise.race([promise1, promise2]).then(function(value) {
  console.log(value);

// make the ajax call to Django server if the refresh rate is greater than zero.
if(refreshRateInt > 0 && value > 0){
  $.ajax({
    url: '/process-url/',
    type: 'get',
    success: function(data) {

    reloadComments(data);
    },
    // in case anything goes wrong with the ajax call.
    failure: function(data) {
        console.log('refreshing comments failed');
    }
    });
  }
  else{
   startRace();
  }
});

}
// Entry point. This function is recalled often.
startRace();


// hide spinner and populate data from GET response to entire page.
// Parameter Data - GET response data.
async function reloadComments(data){

      $('#spinner').hide();

     //reload entire page
     // $("html").html($("html", data).html());

      $("#comments").html(data);
      // make sure theme persists between ajax calls.
       toggleTheme(true);
      $('#comments').show();

      // call entry method again.
      startRace();


}
// method that is called when any ajax call starts.
// currently just for showing the spinner and keeping the dark or light theme.
$( document ).ajaxStart(function() {

  $('#comments').hide();
  $('#spinner').show();
  toggleTheme(true);
});

/* Method toggleTheme. This method allows us the change the theme of the page from dark to light.
Parameter - keep same - This means we just reload the current theme again. 
This is needed after the ajax call.
*/
function toggleTheme(keepSame) {


  
  let themeBtn      = document.getElementById('theme-btn');
  let light         = themeBtn.classList.contains('btn-light');
  let icon          = document.getElementById('theme-btn-icon');
  let container     = document.getElementById('container');
  let comments      = document.getElementsByClassName('list-group-item');
  let dropdownItems = document.getElementsByClassName('dropdown-item');
  let dropdownMenu  = document.getElementsByClassName('dropdown-menu')[0];

   // if currently set to light set to dark and visa versa.
    if(light && !keepSame){
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
      themeBtn.classList.remove('btn-light');
      themeBtn.classList.add('btn-dark');
      container.classList.add('dark');
      dropdownMenu.classList.add('dark');
      document.body.classList.add('dark');
      dropdownMenu.classList.add('dark');
    }
    else if(!keepSame){
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
      themeBtn.classList.remove('btn-dark');
      themeBtn.classList.add('btn-light');
      container.classList.remove('dark');
      dropdownMenu.classList.remove('dark');
      document.body.classList.remove('dark');
      dropdownMenu.classList.remove('dark');
    }
    

  for(let i = 0; i < comments.length; i++){
      if(keepSame){
        if(light){
          comments[i].classList.remove('dark');
        }
        else{
          comments[i].classList.add('dark');
        }
      }
      else{
        if(light){
          comments[i].classList.add('dark');
        }
        else{
          comments[i].classList.remove('dark');
        }
      }   
  }
  for(let i = 0; i < dropdownItems.length; i++){
    if(keepSame){
      if(light){
        dropdownItems[i].classList.remove('dark');
      }
      else{
        dropdownItems[i].classList.add('dark');
      }
    }
    else{
      if(light){
        dropdownItems[i].classList.add('dark');
      }
      else{
        dropdownItems[i].classList.remove('dark');
      }
    }   
  }
  //add body and dropdown styles so it shows correctly after refreshing
  if(keepSame){
    if(light){
      document.body.classList.remove('dark');
      dropdownMenu.classList.remove('dark');
    }
    else{
      document.body.classList.add('dark');
      dropdownMenu.classList.add('dark');
    }
  }

}
