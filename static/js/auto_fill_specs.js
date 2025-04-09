document.addEventListener('DOMContentLoaded', function() {
    const markSelect = document.getElementById('id_mark_name');
    const modelSelect = document.getElementById('id_model_name');
    const form = document.getElementById('ad-form');
console.log('API ыефке:');
    function updateSpecs() {
        const mark = markSelect.value;
        const model = modelSelect.value;

        if (!mark || !model) return;

        fetch(`/api/get-model-specs/?mark=${encodeURIComponent(mark)}&model=${encodeURIComponent(model)}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('API response:', data);

                // Обрабатываем каждое поле отдельно
                updateSelectField('id_fuel_type', data.engine_type);
                updateSelectField('id_gearbox', data.transmission);
                updateSelectField('id_body_type', data.body_type);
                updateSelectField('id_drive', data.drive);
            })
            .catch(error => {
                console.error('Error fetching model specs:', error);
            });
    }

    function updateSelectField(fieldId, dbValues) {
        const select = document.getElementById(fieldId);
        if (!select || !dbValues || dbValues.length === 0) {
            console.log(`No values for field ${fieldId}`);
            return;
        }

        // Если в базе только одно значение для этого поля
        if (dbValues.length === 1) {
            const dbValue = dbValues[0];
            console.log(`Setting single value for ${fieldId}: ${dbValue}`);

            // Ищем option с соответствующим value
            const option = Array.from(select.options).find(opt => opt.value === dbValue);
console.log ("fieldId, dbValues", fieldId, dbValues)
            if (option) {
                option.selected = true;
                select.disabled = true;
                select.classList.add('bg-light');
            } else {
                console.warn(`Value ${dbValue} not found in ${fieldId} options`);
            }
        } else {
            // Если несколько значений - активируем поле
            console.log(`Multiple values for ${fieldId}, enabling selection`);
            select.disabled = false;
            select.classList.remove('bg-light');

            // Можно установить первое значение по умолчанию
            const firstValue = dbValues[0];
            const option = Array.from(select.options).find(opt => opt.value === firstValue);
            if (option) {
                option.selected = true;
            }
        }
    }

    // Слушаем изменения выбора марки и модели
    markSelect.addEventListener('change', updateSpecs);
    modelSelect.addEventListener('change', updateSpecs);

    // Обновляем при загрузке, если значения уже выбраны
    if (markSelect.value && modelSelect.value) {
        updateSpecs();
    }
});