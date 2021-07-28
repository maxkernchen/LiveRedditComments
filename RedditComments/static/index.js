$('#spinner').hide();
// get all bootstrap active cards displayed on the home page
cards = document.getElementsByClassName('active-card');

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
      document.getElementById('form_comment_url').submit();
    });
  }



  