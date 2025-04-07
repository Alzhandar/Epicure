class Modal {
    constructor(modalId) {
      this.modal = document.getElementById(modalId);
      if (!this.modal) return;
      
      this.dialog = this.modal.querySelector('.modal-dialog');
      this.openTriggers = document.querySelectorAll(`[data-bs-toggle="modal"][data-bs-target="#${modalId}"]`);
      this.closeTriggers = this.modal.querySelectorAll('[data-bs-dismiss="modal"], .modal-close');
      this.isOpen = false;
      this.isAnimating = false;
      
      this.init();
    }
    
    init() {
      this.openTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
          e.preventDefault();
          this.open();
        });
      });
      
      this.closeTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
          e.preventDefault();
          this.close();
        });
      });
      
      this.modal.addEventListener('click', (e) => {
        if (e.target === this.modal) {
          this.close();
        }
      });
      
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && this.isOpen) {
          this.close();
        }
      });
    }
    
    open() {
      if (this.isOpen || this.isAnimating) return;
      
      this.isAnimating = true;
      
      document.body.style.overflow = 'hidden'; 
      this.modal.style.display = 'flex';
      
      setTimeout(() => {
        this.modal.classList.add('show');
        this.isOpen = true;
        this.isAnimating = false;
        
        const event = new CustomEvent('modal:opened', { detail: { modalId: this.modal.id } });
        document.dispatchEvent(event);
      }, 50);
    }
    
    close() {
      if (!this.isOpen || this.isAnimating) return;
      
      this.isAnimating = true;
      
      this.modal.classList.remove('show');
      
      setTimeout(() => {
        this.modal.style.display = 'none';
        document.body.style.overflow = ''; 
        this.isOpen = false;
        this.isAnimating = false;
        
        const event = new CustomEvent('modal:closed', { detail: { modalId: this.modal.id } });
        document.dispatchEvent(event);
      }, 300);
    }
    
    static initAll() {
      const modalElements = document.querySelectorAll('.modal');
      const modals = {};
      
      modalElements.forEach(modalEl => {
        const id = modalEl.id;
        if (id) {
          modals[id] = new Modal(id);
        }
      });
      
      return modals;
    }
  }
  
  document.addEventListener('DOMContentLoaded', () => {
    const modals = Modal.initAll();
    
    const cityModal = modals['cityModal'];
    if (cityModal) {
      if (document.body.hasAttribute('data-first-visit')) {
        cityModal.open();
      }
      
      const cityForm = document.querySelector('#cityModal form');
      if (cityForm) {
        const cityInputs = cityForm.querySelectorAll('input[name="city_id"]');
        
        cityInputs.forEach(input => {
          input.addEventListener('change', () => {
            cityForm.querySelector('button[type="submit"]').removeAttribute('disabled');
          });
        });
        
        cityInputs.forEach(input => {
          const label = input.closest('label');
          if (label) {
            label.addEventListener('click', () => {
              cityForm.querySelectorAll('.list-group-item').forEach(item => {
                item.classList.remove('active');
              });
              label.classList.add('active');
            });
          }
        });
      }
    }
  });