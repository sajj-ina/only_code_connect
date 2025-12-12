document.addEventListener('DOMContentLoaded', () => {  

  // SIGN-UP MODAL LOGIC 

  const modal = document.getElementById('signupModal');  

  const openButtons = [document.getElementById('openSignup'), document.getElementById('openSignup2')];  

  const closeButton = document.getElementById('closeSignup');  

  const signupForm = document.getElementById('signupForm');  

  const yearSpan = document.getElementById('year');  

  if (yearSpan) yearSpan.textContent = new Date().getFullYear();  

  function openModal() {  

    modal.setAttribute('aria-hidden', 'false');  

    document.body.style.overflow = 'hidden';  

  }  

  function closeModal() {  

    modal.setAttribute('aria-hidden', 'true');  

    document.body.style.overflow = '';  

  }  

  openButtons.forEach(btn => {  

    if (btn) btn.addEventListener('click', openModal);  

  });  

  
  if (closeButton) closeButton.addEventListener('click', closeModal);  
  modal.addEventListener('click', (e) => {  

    if (e.target === modal) closeModal();  

  });  
 

  // SIGN-IN MODAL LOGIC 

  const signinModal = document.getElementById('signinModal'); 
  const openSignin = document.getElementById('openSignin'); 
  const closeSignin = document.getElementById('closeSignin'); 
  const signinForm = document.getElementById('signinForm'); 

  if (openSignin) openSignin.addEventListener('click', () => { 
    signinModal.setAttribute('aria-hidden', 'false'); 
    document.body.style.overflow = 'hidden'; 

  }); 

  

  if (closeSignin) closeSignin.addEventListener('click', () => { 
    signinModal.setAttribute('aria-hidden', 'true'); 
    document.body.style.overflow = ''; 

  }); 

  if (signinModal) { 
    signinModal.addEventListener('click', (e) => { 

      if (e.target === signinModal) { 

        signinModal.setAttribute('aria-hidden', 'true'); 

        document.body.style.overflow = ''; 

      } 

    }); 

  } 

  if (signinForm) { 

    signinForm.addEventListener('submit', (e) => { 

      e.preventDefault(); 

      const fd = new FormData(signinForm); 
      const email = fd.get('email'); 
      const password = fd.get('password'); 

      let users = JSON.parse(localStorage.getItem('users') || '[]'); 
      const user = users.find(u => u.email === email && u.password === password); 
      if (!user) { 

      alert("Incorrect email or password."); 
      return; 

      } 


      localStorage.setItem("activeUser", JSON.stringify(user)); 
      window.location.href = "dashboard.html"; 

    }); 

  } 
 
  // TAB UI (static) 

  document.querySelectorAll('.tab').forEach(tab => {  

    tab.addEventListener('click', () => {  

      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));  

      tab.classList.add('active');  

    });  

  });  


  // SOCIAL LOGIN DEMO 

  document.querySelectorAll('.btn.social').forEach(btn => {  

    btn.addEventListener('click', () => {  

      alert(`Demo Login: ${btn.textContent}\n\n(Full OAuth will work once backend is added.)`);  

    });  

  });  


  // LOCAL STORAGE SIGN-UP 

  if (signupForm) { 

    signupForm.addEventListener('submit', (e) => {  

      e.preventDefault();  

      const fd = new FormData(signupForm);  

      const data = {  

        name: fd.get('name'),  
        email: fd.get('email'),  
        password: fd.get('password')  

      };  

      const submitBtn = signupForm.querySelector('button[type="submit"]');  
      submitBtn.disabled = true;  
      submitBtn.textContent = 'Creating…';  
      let users = JSON.parse(localStorage.getItem('users') || '[]');  

      if (users.some(u => u.email === data.email)) {  

        alert('This email is already registered.');  

        submitBtn.disabled = false;  

        submitBtn.textContent = 'Create Account';  

        return;  

      }  

      users.push(data);  

      localStorage.setItem('users', JSON.stringify(users));  
      alert('Account created successfully! (Stored in your browser)');  

      signupForm.reset();  

      closeModal();  

      submitBtn.disabled = false;  

      submitBtn.textContent = 'Create Account';  

      window.location.href = 'dashboard.html';  

    }); 

  } 

  //NAVIGATION JS 

  const nav = document.querySelector('.glass-nav'); 

  const toggle = document.getElementById('navToggle'); 

  const mobileMenu = document.getElementById('mobileMenu'); 

  

  window.addEventListener('scroll', () => { 

    if (nav) { 

      if (window.scrollY > 30) nav.classList.add('scrolled'); 

      else nav.classList.remove('scrolled'); 

    } 

  }); 

  

  if (toggle && mobileMenu) { 

    toggle.addEventListener('click', () => { 

      mobileMenu.classList.toggle('show'); 

    }); 

  } 

  

  // Hook nav buttons to modal 

  const navSignup = document.getElementById('navSignup'); 

  const mobileSignup = document.getElementById('mobileSignup'); 

  

  if (navSignup && openButtons[0]) { 

    navSignup.addEventListener('click', () => openButtons[0].click()); 

  } 

  if (mobileSignup && openButtons[0]) { 

    mobileSignup.addEventListener('click', () => openButtons[0].click()); 

  } 

  const navLogin = document.getElementById('navLogin'); 

  const mobileLogin = document.getElementById('mobileLogin'); 

  if (navLogin && openSignin) navLogin.addEventListener('click', () => openSignin.click()); 

  if (mobileLogin && openSignin) mobileLogin.addEventListener('click', () => openSignin.click()); 

}); 

 