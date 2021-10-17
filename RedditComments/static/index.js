$('#spinner').hide();
// get all bootstrap active cards displayed on the home page
cards = document.getElementsByClassName('active-card');

var offset = new Date().getTimezoneOffset();


// Loop through each card and add an event listener in its link element at the bottom.
// This event when triggered will fill in the form and submit it with the submission the card represents.
// It will also hide the input form and display a loading message/icon.
for(let i = 0; i < cards.length; i++){
    let cardTemp = cards[i];
    let hiddenLink = cardTemp.getElementsByClassName('hidden')[0].innerHTML;
    let link = cardTemp.getElementsByClassName('link')[0]
    link.addEventListener('click', function (event) {
      $('#all-input-container').hide();
      $('#spinner').show();
      let formInput = document.getElementById('reddit_url');
      formInput.value = hiddenLink;
      $('#form_comment_url').submit();
    });
}

$("#form_comment_url").submit(function( event ) {
 let formInput = document.getElementById('reddit_url');

 $("#form_comment_url").append('<input type="hidden" name="time_zone_offset" value="' + offset + '" />');
 // change url to include submission id
 $('#form_comment_url').attr('action', getSubmissionId(formInput.value));
});

// add the submission id to the processing url. This is so we have a unique url which allows the user to open
// multiple sessions for different streams of comments.
function getSubmissionId(redditUrl){
    let subId = "/process-url/";
    let index = redditUrl.toLowerCase().search("comments")
    if(index >= 0){
      subId += redditUrl.substr(index + 9, 6) + "/";
    }
    return subId;
}



  