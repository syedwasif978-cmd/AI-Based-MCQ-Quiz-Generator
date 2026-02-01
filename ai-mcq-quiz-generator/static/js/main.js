document.addEventListener('DOMContentLoaded', function(){
  // smooth link transitions
  document.querySelectorAll('a').forEach(a=>{
    if(a.href && a.target!=='_blank'){
      a.addEventListener('click', (e)=>{
        // add small fade-out on navigation for internal links
        const url = new URL(a.href);
        if(url.origin===location.origin){
          e.preventDefault();
          document.body.style.transition = 'opacity .25s ease';
          document.body.style.opacity = '0.0';
          setTimeout(()=> location.href = a.href, 220);
        }
      })
    }
  })

  // enhance forms with submit spinner
  const forms = document.querySelectorAll('form');
  forms.forEach(form=>{
    form.addEventListener('submit', function(e){
      const submit = form.querySelector('button[type=submit]');
      if(submit){
        submit.disabled = true;
        const spinner = document.createElement('span');
        spinner.className = 'spinner';
        spinner.style.marginLeft = '8px';
        submit.appendChild(spinner);
      }
    })
  })

  // small fade-in for content
  document.querySelectorAll('.card, .hero-card').forEach(el=>el.classList.add('fade-in'))
})