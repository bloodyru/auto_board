// Элементы выбора марки и модели автомобиля
const brandSelect = document.getElementById("id_mark_name");
const modelSelect = document.getElementById("id_model_name");

document.addEventListener("DOMContentLoaded", function () {
 // Обработчик изменения выбранной марки автомобиля
 brandSelect.addEventListener("change", function () {
    const selectedBrand = brandSelect.value;
    console.log(selectedBrand)
    // Очищаем список моделей
    modelSelect.innerHTML = "<option value=''>Выберите модель</option>";

    if (selectedBrand) {
        console.log("Выбрана марка:", selectedBrand);
        // Загружаем модели для выбранной марки
        fetch(`/get_models/?brand=${selectedBrand}`)
            .then(response => response.json())
            .then(data => {
                console.log("Получены модели:", data.models);
                // Заполняем список моделей
                data.models.forEach(model => {
                    const option = document.createElement("option");
                    option.value = model;
                    option.textContent = model;
                    modelSelect.appendChild(option);
                });
            })
            .catch(error => console.error("Ошибка загрузки моделей:", error));
    }
});
});
