$('#spinner').hide();

cards = document.getElementsByClassName('active-card');

for(var i = 0;i < cards.length;i++ ){
    let cardTemp = cards[i];
    let hiddenLink = cardTemp.getElementsByClassName('hidden')[0].innerHTML;
    let link = cardTemp.getElementsByClassName('link')[0]
    link.addEventListener('click', function (event) {
      $('#all-input-div').hide();
      $('#spinner').show();
      let formInput = document.getElementById('reddit_url');
      formInput.value = hiddenLink;
      document.getElementById('form_comment_url').submit();
    });
  }



  