$('#spinner').hide();
$('#refresh-btn').hide();

// bool for when we scrolled down, this for tracking if we should refresh or not.
// Similar to youtube or twitch comments where scrolling stops the refreshing. 
var scrolledDown = false;
/* Create two promises that will race each other.
1. promise1 - This promise is only resolved if refresh rate is not "Don't Refresh" ( > 0).
              It is resolved after the amount of the time the refresh rate is defined for passes.
               Then we will call ajax to reload the comments in page.
2. promise2 - This promise is resolved whenever the refresh rate drop down has changed value.
                This means that if the refresh rate is changed while we are waiting for a new refresh, the current
               refresh wait time is reset.
3. promise3 - This promise is resolved when the refresh floating button is clicked, will immediately reload comments.
              It will only resolve if the refresh button is visible which is when we scroll down on the comment 
              list past the refresh options.

*/

async function startRace (){
// get current refresh rate if refresh rate < 0 we don't refresh.
let refreshRateSelect = document.getElementById("refresh-rate-options");
let refreshRateInt = refreshRateSelect.options[refreshRateSelect.selectedIndex].value;

let promise1 = new Promise(function(resolve) {
  console.log("in Promise1");
  // only resolve this promise if refresh rate is not set to don't refresh.'
  // resolve after the amount of time defined in the refresh rate drop down.
    if(refreshRateInt > 0 && !scrolledDown)
    {
      setTimeout(resolve, refreshRateInt, '1');
    }
    else{
      // resolve after 2 seconds so we are not calling too often
      // to check if we have scrolled back up to the top
      setTimeout(resolve, 2000, '-3');;
    }
  
});

// second promise which is resolved whenever the refresh rate drop is changed.
let promise2 = new Promise(function(resolve) {
    $("#refresh-rate-options").change(function(){
      console.log("in Promise2");
    // resolve with -2 as other values have been taken by the refresh rate promise1.
        resolve('-2');
    });
});

let promise3 = new Promise(function(resolve) {
  $("#refresh-btn").click(function(){
      console.log("in Promise3");
      resolve('2');
  });
});

Promise.race([promise1, promise2, promise3]).then(function(value) {
  console.log(value);

// make the ajax call to Django server if we have a > 0 refresh rate
// and we have not scrolled to where the manual refresh button is showing
// or if we were called from the refresh button manually
if((refreshRateInt > 0 && value > 0 && !scrolledDown) || value == 2){
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

      $('#comments').html(data);
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

// use bootstrap select built-in event to trigger themes for drop down menus
$('#refresh-rate-options').on('show.bs.select', applyDropDownStyle);


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
 
  // if currently set to light set to dark and visa versa.
  if(light && !keepSame){
    icon.classList.remove('fa-sun');
    icon.classList.add('fa-moon');
    themeBtn.classList.remove('btn-light');
    themeBtn.classList.add('btn-dark');
    container.classList.add('dark');
    document.body.classList.add('dark');
    
  }
  else if(!keepSame){
    icon.classList.remove('fa-moon');
    icon.classList.add('fa-sun');
    themeBtn.classList.remove('btn-dark');
    themeBtn.classList.add('btn-light');
    container.classList.remove('dark');
    document.body.classList.remove('dark');
    
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
 
  //add body styles so it shows correctly during refresh
  if(keepSame){
    if(light){
      document.body.classList.remove('dark');
    }
    else{
      document.body.classList.add('dark');
    }
  }

}
/*Apply drop down styles when clicked
  Doing it this way rather than changing on refresh/theme button, 
  because the elements that need styles applied are only found when the drop down is at least clicked once.
  That means if a user were to change to dark theme 
  and then click the drop down for the first time, it would still be in light theme.
*/
function applyDropDownStyle(){

  let themeBtn      = document.getElementById('theme-btn');
  let light         = themeBtn.classList.contains('btn-light');
  let dropdownItems = document.getElementsByClassName('dropdown-item');
  let dropdownMenu  = document.getElementsByClassName('dropdown-menu')[0];
  
  if(light){
     dropdownMenu.classList.remove('dark'); 
     for(let i = 0; i < dropdownItems.length; i++){
          dropdownItems[i].classList.remove('dark');
     } 
  }
  else{
    dropdownMenu.classList.add('dark');
    for(let i = 0; i < dropdownItems.length; i++){
        dropdownItems[i].classList.add('dark');
    } 
  }
}

var commentDiv = document.getElementById('comments');

function scrollListener(){
  if(window.scrollY > commentDiv.offsetTop){
    scrolledDown = true;
    $('#refresh-btn').show();

  }
  else if(window.scrollY <= commentDiv.offsetTop){
    scrolledDown = false;
    $('#refresh-btn').hide();
  }
  
} 

window.addEventListener('scroll', scrollListener);