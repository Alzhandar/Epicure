const header = document.getElementById('header');
const dropdowns = document.querySelectorAll('.dropdown');

document.addEventListener('DOMContentLoaded', () => {
  initScrollEffects();
  initDropdowns();
  initAlertDismiss();
  
  initFadeEffects();
});

function initScrollEffects() {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });
}

function initDropdowns() {
  dropdowns.forEach(dropdown => {
    const button = dropdown.querySelector('.dropdown-toggle');
    const menu = dropdown.querySelector('.dropdown-menu');
    
    button.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      
      dropdowns.forEach(other => {
        if (other !== dropdown) {
          other.querySelector('.dropdown-menu').classList.remove('show');
        }
      });
      
      menu.classList.toggle('show');
    });
  });
  
  document.addEventListener('click', (e) => {
    dropdowns.forEach(dropdown => {
      if (!dropdown.contains(e.target)) {
        dropdown.querySelector('.dropdown-menu').classList.remove('show');
      }
    });
  });
}

function initAlertDismiss() {
  document.querySelectorAll('.alert .close').forEach(button => {
    button.addEventListener('click', function() {
      const alert = this.closest('.alert');
      alert.classList.remove('fade-in');
      alert.classList.add('fade-out');
      
      setTimeout(() => {
        alert.remove();
      }, 300);
    });
  });
  
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
      alert.classList.remove('fade-in');
      alert.classList.add('fade-out');
      
      setTimeout(() => {
        alert.remove();
      }, 300);
    });
  }, 5000);
}

function initFadeEffects() {
  const fadeElements = document.querySelectorAll('.fade-in-element');
  
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    
    fadeElements.forEach(element => {
      observer.observe(element);
    });
  } else {
    fadeElements.forEach(element => {
      element.classList.add('fade-in');
    });
  }
}

function smoothScrollTo(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    window.scrollTo({
      top: element.offsetTop - 80, 
      behavior: 'smooth'
    });
  }
}