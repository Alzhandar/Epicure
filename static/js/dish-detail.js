document.addEventListener('DOMContentLoaded', function() {
    initDishDetailModal();
});

function initDishDetailModal() {
    // Получаем модальное окно
    const modal = document.getElementById('dishDetailModal');
    if (!modal) return;
    
    // Проверяем, определен ли bootstrap
    if (typeof bootstrap === 'undefined') {
        console.error('Bootstrap JS не загружен. Модальные окна не будут работать.');
        return;
    }
    
    const modalInstance = new bootstrap.Modal(modal);
    const loadingSection = modal.querySelector('.dish-detail-loading');
    const contentSection = modal.querySelector('.dish-detail-loaded');
    const errorSection = modal.querySelector('.dish-detail-error');
    
    console.log('Инициализация модального окна блюд');
    
    // Находим элементы для заполнения
    const dishImage = modal.querySelector('.dish-detail-image');
    const dishTitle = modal.querySelector('.dish-detail-title');
    const dishType = modal.querySelector('.dish-detail-type');
    const dishPrice = modal.querySelector('.dish-detail-price');
    const dishDescription = modal.querySelector('.dish-detail-description');
    const caloriesValue = modal.querySelector('.calories-value');
    const proteinsValue = modal.querySelector('.proteins-value');
    const fatsValue = modal.querySelector('.fats-value');
    const carbsValue = modal.querySelector('.carbs-value');
    const restaurantName = modal.querySelector('.dish-detail-restaurant-name');
    const orderButton = modal.querySelector('.modal-dish-order-btn');
    
    // Отладка - проверяем, находит ли селектор наши триггеры
    const triggers = document.querySelectorAll('.dish-modal-trigger, .dish-more-btn');
    console.log('Найдено триггеров для модального окна:', triggers.length);
    
    // Добавляем обработчики для всех триггеров
    triggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            console.log('Клик по блюду или кнопке подробнее');
            
            // Если это кнопка "подробнее", останавливаем всплытие события
            if (e.currentTarget.classList.contains('dish-more-btn')) {
                e.stopPropagation();
            }
            
            // Находим ID блюда
            const dishId = this.dataset.dishId || this.closest('.dish-card').dataset.dishId;
            console.log('ID выбранного блюда:', dishId);
            
            if (!dishId) {
                console.error('ID блюда не найден');
                return;
            }
            
            // Показываем модальное окно и загружаем данные
            modalInstance.show();
            loadDishDetails(dishId);
        });
    });
    
    // Функция для загрузки данных о блюде
    function loadDishDetails(dishId) {
        // Показываем индикатор загрузки
        loadingSection.style.display = 'flex';
        contentSection.style.display = 'none';
        errorSection.style.display = 'none';
        
        // URL для запроса данных
        const apiUrl = `/products/dish/${dishId}/`;
        console.log('Загрузка данных блюда с URL:', apiUrl);
        
        // Запрос к API
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Ошибка HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Получены данные о блюде:', data);
                
                // Заполняем детали блюда
                dishTitle.textContent = data.name;
                dishType.textContent = data.menu_type;
                dishPrice.textContent = `${data.price} ₸`;
                dishDescription.textContent = data.description;
                
                // Заполняем данные о пищевой ценности
                caloriesValue.textContent = data.nutrition.calories + (data.nutrition.calories !== 'Н/Д' ? ' ккал' : '');
                proteinsValue.textContent = data.nutrition.proteins + (data.nutrition.proteins !== 'Н/Д' ? ' г' : '');
                fatsValue.textContent = data.nutrition.fats + (data.nutrition.fats !== 'Н/Д' ? ' г' : '');
                carbsValue.textContent = data.nutrition.carbohydrates + (data.nutrition.carbohydrates !== 'Н/Д' ? ' г' : '');
                
                // Заполняем данные о ресторане
                restaurantName.textContent = data.restaurant.name;
                
                // Устанавливаем изображение, если оно есть
                if (data.image) {
                    dishImage.src = data.image;
                    dishImage.alt = data.name;
                    dishImage.parentElement.style.display = 'block';
                } else {
                    dishImage.parentElement.style.display = 'none';
                }
                
                // Если есть кнопка заказа, добавляем data-атрибут с ID блюда
                if (orderButton) {
                    orderButton.dataset.dishId = data.id;
                }
                
                // Показываем контент и скрываем загрузку
                loadingSection.style.display = 'none';
                contentSection.style.display = 'block';
            })
            .catch(error => {
                console.error('Ошибка при загрузке данных блюда:', error);
                
                // Показываем сообщение об ошибке
                errorSection.querySelector('.error-message').textContent = 
                    'Не удалось загрузить информацию о блюде. Пожалуйста, попробуйте позже.';
                loadingSection.style.display = 'none';
                errorSection.style.display = 'block';
            });
    }
    
    if (orderButton) {
        orderButton.addEventListener('click', function() {
            const dishId = this.dataset.dishId;
            if (!dishId) return;
            
            console.log(`Блюдо с ID ${dishId} добавлено в заказ из модального окна`);
            
            showNotification('Блюдо добавлено в заказ');
            
            modalInstance.hide();
        });
    }
}

function showNotification(message) {
    let notification = document.querySelector('.toast-notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.className = 'toast-notification';
        notification.innerHTML = `
          <div class="toast-content">
            <i class="fas fa-check-circle toast-icon"></i>
            <span>${message}</span>
          </div>
        `;
        
        document.body.appendChild(notification);
        
        if (!document.querySelector('#toast-notification-style')) {
            const style = document.createElement('style');
            style.id = 'toast-notification-style';
            style.textContent = `
                .toast-notification {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background-color: var(--color-primary, #000);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
            `;
            document.head.appendChild(style);
        }
    } else {
        notification.querySelector('span').textContent = message;
    }
    
    setTimeout(() => notification.classList.add('show'), 10);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}