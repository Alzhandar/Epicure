document.addEventListener('DOMContentLoaded', function() {
    initDishesCarousel();
    
    initOrderButtons();
  });
  
  function initDishesCarousel() {
    const carousel = document.getElementById('dishesCarousel');
    if (!carousel) return;
    
    const leftButton = document.querySelector('.scroll-left');
    const rightButton = document.querySelector('.scroll-right');
    
    if (leftButton && rightButton) {
      leftButton.addEventListener('click', () => {
        const scrollAmount = carousel.offsetWidth * 0.75;
        carousel.scrollBy({
          left: -scrollAmount,
          behavior: 'smooth'
        });
      });
      
      rightButton.addEventListener('click', () => {
        const scrollAmount = carousel.offsetWidth * 0.75;
        carousel.scrollBy({
          left: scrollAmount,
          behavior: 'smooth'
        });
      });
      
      carousel.addEventListener('scroll', updateScrollButtons);
      
      updateScrollButtons();
    }
    
    let touchStartX = 0;
    let touchEndX = 0;
    
    carousel.addEventListener('touchstart', e => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    
    carousel.addEventListener('touchend', e => {
      touchEndX = e.changedTouches[0].screenX;
      handleSwipe();
    }, { passive: true });
    
    function handleSwipe() {
      const scrollAmount = carousel.offsetWidth * 0.5;
      const distance = touchStartX - touchEndX;
      
      if (distance > 50) {
        carousel.scrollBy({
          left: scrollAmount,
          behavior: 'smooth'
        });
      } else if (distance < -50) {
        carousel.scrollBy({
          left: -scrollAmount,
          behavior: 'smooth'
        });
      }
    }
    
    function updateScrollButtons() {
      if (!leftButton || !rightButton) return;
      
      const scrollLeft = carousel.scrollLeft;
      const maxScrollLeft = carousel.scrollWidth - carousel.clientWidth;
      
      leftButton.style.opacity = scrollLeft <= 10 ? '0.5' : '1';
      leftButton.style.pointerEvents = scrollLeft <= 10 ? 'none' : 'auto';
      
      rightButton.style.opacity = scrollLeft >= maxScrollLeft - 10 ? '0.5' : '1';
      rightButton.style.pointerEvents = scrollLeft >= maxScrollLeft - 10 ? 'none' : 'auto';
    }
  }
  
  function initOrderButtons() {
    const orderButtons = document.querySelectorAll('.dish-order-btn');
    
    orderButtons.forEach(button => {
      button.addEventListener('click', function() {
        const dishId = this.getAttribute('data-dish-id');
        
        this.classList.add('clicked');
        setTimeout(() => this.classList.remove('clicked'), 200);
        
        console.log(`Блюдо с ID ${dishId} добавлено в заказ`);
        
        showNotification('Блюдо добавлено в заказ');
      });
    });
  }
  
  function showNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'toast-notification';
    notification.innerHTML = `
      <div class="toast-content">
        <i class="fas fa-check-circle toast-icon"></i>
        <span>${message}</span>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
  
  const toastStyle = document.createElement('style');
  toastStyle.textContent = `
  .toast-notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: var(--color-primary);
    color: white;
    padding: 12px 16px;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    transform: translateY(100%);
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 9999;
  }
  
  .toast-notification.show {
    transform: translateY(0);
    opacity: 1;
  }
  
  .toast-content {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .toast-icon {
    color: #4cd964;
  }
  
  .dish-order-btn.clicked {
    transform: scale(0.9);
  }
  `;
  document.head.appendChild(toastStyle);