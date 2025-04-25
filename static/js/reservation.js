class ReservationService {
    constructor(baseUrl = '/api/room/') {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        };
    }

    /**
     * Устанавливает токен авторизации для защищенных запросов
     * @param {string} token - JWT токен
     */
    setAuthToken(token) {
        if (token) {
            this.headers['Authorization'] = `Bearer ${token}`;
        } else {
            delete this.headers['Authorization'];
        }
    }

    /**
     * Получает список всех ресторанов
     * @returns {Promise} Promise с данными о ресторанах
     */
    async getRestaurants() {
        try {
            const response = await fetch('/api/restaurant/restaurants/', {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Ошибка при загрузке ресторанов:', error);
            throw error;
        }
    }

    /**
     * Получает список столов в выбранном ресторане
     * @param {number} restaurantId - ID ресторана
     * @returns {Promise} Promise с данными о столах
     */
    async getRestaurantTables(restaurantId) {
        try {
            const response = await fetch(`${this.baseUrl}restaurant/${restaurantId}/tables/`, {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при загрузке столов для ресторана ${restaurantId}:`, error);
            throw error;
        }
    }

    /**
     * Проверяет доступность столов на конкретную дату
     * @param {Object} data - Данные для проверки
     * @returns {Promise} Promise с данными о доступности столов
     */
    async checkTableAvailability(data) {
        try {
            const response = await fetch(`${this.baseUrl}availability/`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Ошибка при проверке доступности столов:', error);
            throw error;
        }
    }

    /**
     * Получает доступные временные слоты для конкретного стола и даты
     * @param {number} restaurantId - ID ресторана
     * @param {string} tableId - UUID стола
     * @param {string} date - Дата в формате YYYY-MM-DD
     * @returns {Promise} Promise с данными о доступных временных слотах
     */
    async getAvailableTimeSlots(restaurantId, tableId, date) {
        try {
            const url = new URL(`${this.baseUrl}available-times/`, window.location.origin);
            url.searchParams.append('restaurant', restaurantId);
            url.searchParams.append('table', tableId);
            url.searchParams.append('date', date);
            
            const response = await fetch(url, {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Ошибка при получении доступных временных слотов:', error);
            throw error;
        }
    }

    /**
     * Создает новое бронирование
     * @param {Object} reservationData - Данные бронирования
     * @returns {Promise} Promise с данными созданного бронирования
     */
    async createReservation(reservationData) {
        try {
            const response = await fetch(`${this.baseUrl}reservations/`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(reservationData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw {
                    status: response.status,
                    data: data
                };
            }
            
            return data;
        } catch (error) {
            console.error('Ошибка при создании бронирования:', error);
            throw error;
        }
    }

    /**
     * Отменяет бронирование
     * @param {number} reservationId - ID бронирования
     * @returns {Promise} Promise с результатом операции
     */
    async cancelReservation(reservationId) {
        try {
            const response = await fetch(`${this.baseUrl}cancel/${reservationId}/`, {
                method: 'POST',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Ошибка при отмене бронирования ${reservationId}:`, error);
            throw error;
        }
    }

    /**
     * Получает бронирования пользователя по email или телефону
     * @param {Object} params - Параметры запроса (email или phone)
     * @returns {Promise} Promise с данными о бронированиях пользователя
     */
    async getMyReservations(params) {
        try {
            const url = new URL(`${this.baseUrl}reservations/my_reservations/`, window.location.origin);
            
            if (params.email) {
                url.searchParams.append('email', params.email);
            }
            if (params.phone) {
                url.searchParams.append('phone', params.phone);
            }
            
            const response = await fetch(url, {
                method: 'GET',
                headers: this.headers
            });
            
            if (!response.ok) {
                throw new Error(`Ошибка HTTP: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Ошибка при получении бронирований:', error);
            throw error;
        }
    }
}

/**
 * UI-контроллер для работы с формой бронирования
 */
class ReservationFormController {
    constructor(formId, service) {
        this.form = document.getElementById(formId);
        if (!this.form) {
            console.error(`Форма с ID ${formId} не найдена`);
            return;
        }
        
        this.service = service || new ReservationService();
        this.restaurantSelect = this.form.querySelector('#restaurant');
        this.dateInput = this.form.querySelector('#reservation_date');
        this.sectionSelect = this.form.querySelector('#section');
        this.tableSelect = this.form.querySelector('#table');
        this.timeSlotSelect = this.form.querySelector('#time_slot');
        this.guestCountInput = this.form.querySelector('#guest_count');
        this.guestNameInput = this.form.querySelector('#guest_name');
        this.guestPhoneInput = this.form.querySelector('#guest_phone');
        this.guestEmailInput = this.form.querySelector('#guest_email');
        this.specialRequestsInput = this.form.querySelector('#special_requests');
        this.submitButton = this.form.querySelector('button[type="submit"]');
        
        this.errorContainer = document.createElement('div');
        this.errorContainer.className = 'alert alert-danger d-none';
        this.form.prepend(this.errorContainer);
        
        this.successContainer = document.createElement('div');
        this.successContainer.className = 'alert alert-success d-none';
        this.form.prepend(this.successContainer);
        
        this.initEventListeners();
    }
    
    /**
     * Инициализирует обработчики событий для формы
     */
    initEventListeners() {
        // Загрузка ресторанов при инициализации
        this.loadRestaurants();
        
        // Обработчики событий изменения значений в форме
        if (this.restaurantSelect) {
            this.restaurantSelect.addEventListener('change', () => this.loadRestaurantTables());
        }
        
        if (this.sectionSelect) {
            this.sectionSelect.addEventListener('change', () => this.loadTablesForSection());
        }
        
        if (this.tableSelect && this.dateInput) {
            const loadTimeSlots = () => {
                if (this.tableSelect.value && this.dateInput.value) {
                    this.loadTimeSlots();
                }
            };
            
            this.tableSelect.addEventListener('change', loadTimeSlots);
            this.dateInput.addEventListener('change', loadTimeSlots);
        }
        
        // Обработчик отправки формы
        this.form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm();
        });
    }
    
    /**
     * Загружает список ресторанов
     */
    async loadRestaurants() {
        if (!this.restaurantSelect) return;
        
        try {
            this.restaurantSelect.disabled = true;
            this.restaurantSelect.innerHTML = '<option value="">Загрузка...</option>';
            
            const restaurants = await this.service.getRestaurants();
            
            this.restaurantSelect.innerHTML = '<option value="">Выберите ресторан</option>';
            restaurants.forEach(restaurant => {
                const option = document.createElement('option');
                option.value = restaurant.id;
                option.textContent = restaurant.name;
                this.restaurantSelect.appendChild(option);
            });
        } catch (error) {
            this.showError('Не удалось загрузить список ресторанов');
        } finally {
            this.restaurantSelect.disabled = false;
        }
    }
    
    /**
     * Загружает информацию о секциях и столах в выбранном ресторане
     */
    async loadRestaurantTables() {
        if (!this.restaurantSelect || !this.restaurantSelect.value) {
            this.resetSelects([this.sectionSelect, this.tableSelect, this.timeSlotSelect]);
            return;
        }
        
        const restaurantId = this.restaurantSelect.value;
        
        try {
            this.sectionSelect.disabled = true;
            this.sectionSelect.innerHTML = '<option value="">Загрузка...</option>';
            
            const data = await this.service.getRestaurantTables(restaurantId);
            
            this.sectionSelect.innerHTML = '<option value="">Выберите секцию</option>';
            data.sections.forEach(section => {
                const option = document.createElement('option');
                option.value = section.id;
                option.textContent = section.name;
                option.dataset.tables = JSON.stringify(section.tables);
                this.sectionSelect.appendChild(option);
            });
            
            this.resetSelects([this.tableSelect, this.timeSlotSelect]);
        } catch (error) {
            this.showError('Не удалось загрузить информацию о столах');
        } finally {
            this.sectionSelect.disabled = false;
        }
    }
    
    /**
     * Загружает столы для выбранной секции
     */
    loadTablesForSection() {
        if (!this.sectionSelect || !this.sectionSelect.value) {
            this.resetSelects([this.tableSelect, this.timeSlotSelect]);
            return;
        }
        
        const selectedOption = this.sectionSelect.options[this.sectionSelect.selectedIndex];
        if (!selectedOption.dataset.tables) {
            this.resetSelects([this.tableSelect, this.timeSlotSelect]);
            return;
        }
        
        try {
            const tables = JSON.parse(selectedOption.dataset.tables);
            
            this.tableSelect.innerHTML = '<option value="">Выберите стол</option>';
            tables.forEach(table => {
                const option = document.createElement('option');
                option.value = table.id;
                option.textContent = `Стол №${table.number}`;
                this.tableSelect.appendChild(option);
            });
            
            this.resetSelects([this.timeSlotSelect]);
        } catch (error) {
            this.showError('Ошибка при загрузке столов');
        }
    }
    
    /**
     * Загружает доступные временные слоты для выбранного стола и даты
     */
    async loadTimeSlots() {
        if (!this.restaurantSelect.value || !this.tableSelect.value || !this.dateInput.value) {
            this.resetSelects([this.timeSlotSelect]);
            return;
        }
        
        const restaurantId = this.restaurantSelect.value;
        const tableId = this.tableSelect.value;
        const date = this.dateInput.value;
        
        try {
            this.timeSlotSelect.disabled = true;
            this.timeSlotSelect.innerHTML = '<option value="">Загрузка...</option>';
            
            const slots = await this.service.getAvailableTimeSlots(restaurantId, tableId, date);
            
            this.timeSlotSelect.innerHTML = '<option value="">Выберите время</option>';
            slots.forEach(slot => {
                if (slot.available) {
                    const startTime = this.formatTime(slot.start_time);
                    const endTime = this.formatTime(slot.end_time);
                    
                    const option = document.createElement('option');
                    option.value = JSON.stringify({
                        start_time: slot.start_time,
                        end_time: slot.end_time
                    });
                    option.textContent = `${startTime} - ${endTime}`;
                    this.timeSlotSelect.appendChild(option);
                }
            });
            
            if (this.timeSlotSelect.options.length <= 1) {
                const option = document.createElement('option');
                option.disabled = true;
                option.textContent = 'Нет доступных слотов на выбранную дату';
                this.timeSlotSelect.appendChild(option);
            }
        } catch (error) {
            this.showError('Не удалось загрузить доступные временные слоты');
        } finally {
            this.timeSlotSelect.disabled = false;
        }
    }
    
    /**
     * Отправляет форму бронирования
     */
    async submitForm() {
        this.hideMessages();
        
        if (!this.validateForm()) {
            return;
        }
        
        const timeSlot = JSON.parse(this.timeSlotSelect.value);
        
        const reservationData = {
            restaurant: parseInt(this.restaurantSelect.value),
            table: this.tableSelect.value,
            reservation_date: this.dateInput.value,
            start_time: timeSlot.start_time,
            end_time: timeSlot.end_time,
            guest_count: parseInt(this.guestCountInput.value),
            guest_name: this.guestNameInput.value,
            guest_phone: this.guestPhoneInput.value,
            guest_email: this.guestEmailInput.value || null,
            special_requests: this.specialRequestsInput.value || null
        };
        
        try {
            this.submitButton.disabled = true;
            this.submitButton.textContent = 'Отправка...';
            
            const result = await this.service.createReservation(reservationData);
            
            this.showSuccess('Бронирование успешно создано!');
            this.form.reset();
            this.resetSelects([this.sectionSelect, this.tableSelect, this.timeSlotSelect]);
            
            // Перенаправление на страницу подтверждения или другие действия
            if (window.reservationSuccess) {
                window.reservationSuccess(result);
            }
        } catch (error) {
            if (error.data) {
                const errorMessages = [];
                Object.entries(error.data).forEach(([field, messages]) => {
                    if (Array.isArray(messages)) {
                        messages.forEach(msg => errorMessages.push(msg));
                    } else {
                        errorMessages.push(`${field}: ${messages}`);
                    }
                });
                this.showError(errorMessages.join('<br>'));
            } else {
                this.showError('Произошла ошибка при создании бронирования');
            }
        } finally {
            this.submitButton.disabled = false;
            this.submitButton.textContent = 'Забронировать';
        }
    }
    
    /**
     * Проверяет валидность формы
     * @returns {boolean} Результат валидации
     */
    validateForm() {
        const requiredFields = [
            { elem: this.restaurantSelect, message: 'Выберите ресторан' },
            { elem: this.dateInput, message: 'Выберите дату' },
            { elem: this.sectionSelect, message: 'Выберите секцию' },
            { elem: this.tableSelect, message: 'Выберите стол' },
            { elem: this.timeSlotSelect, message: 'Выберите время' },
            { elem: this.guestCountInput, message: 'Укажите количество гостей' },
            { elem: this.guestNameInput, message: 'Введите имя' },
            { elem: this.guestPhoneInput, message: 'Введите номер телефона' }
        ];
        
        for (const field of requiredFields) {
            if (!field.elem || !field.elem.value) {
                this.showError(field.message);
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * Отображает сообщение об ошибке
     * @param {string} message - Текст ошибки
     */
    showError(message) {
        this.errorContainer.innerHTML = message;
        this.errorContainer.classList.remove('d-none');
        this.successContainer.classList.add('d-none');
    }
    
    /**
     * Отображает сообщение об успехе
     * @param {string} message - Текст сообщения
     */
    showSuccess(message) {
        this.successContainer.innerHTML = message;
        this.successContainer.classList.remove('d-none');
        this.errorContainer.classList.add('d-none');
    }
    
    /**
     * Скрывает все информационные сообщения
     */
    hideMessages() {
        this.errorContainer.classList.add('d-none');
        this.successContainer.classList.add('d-none');
    }
    
    /**
     * Сбрасывает выбранные значения в указанных select-элементах
     * @param {Array} selects - Массив select-элементов для сброса
     */
    resetSelects(selects) {
        selects.forEach(select => {
            if (select) {
                select.innerHTML = '<option value="">Выберите значение</option>';
            }
        });
    }
    
    /**
     * Форматирует время для отображения
     * @param {string} time - Время в формате HH:MM:SS
     * @returns {string} Отформатированное время в формате HH:MM
     */
    formatTime(time) {
        return time.substring(0, 5);
    }
}

// Экспорт классов для использования в других модулях
window.ReservationService = ReservationService;
window.ReservationFormController = ReservationFormController;