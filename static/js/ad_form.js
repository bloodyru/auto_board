window.addEventListener('load', function() {

const inputElement = document.getElementById('images');
const previewContainer = document.getElementById('image-preview');

const fileMap = new Map(); // {index: {file, element}}
let index = 1;
//index = performance.now(); // Еще более точный

let cropper;
let currentCropIndex = 0;
const cropModal = new bootstrap.Modal(document.getElementById("cropModal"));
const cropImage = document.getElementById("crop-image");

const adForm = document.getElementById('ad-form');

const MAX_FILES = 10;

inputElement.addEventListener('change', function (event) {
    const files = Array.from(event.target.files)
        .filter(file => file.type.match('image.*'));

    if (fileMap.size + files.length > MAX_FILES) {
        alert(`Можно загрузить не более ${MAX_FILES} файлов`);
        return;
    }

    files.forEach((file) => {
        addImageToMap(file, getNextIndex());
    });
});


function getNextIndex() {
    while (fileMap.has(index)) index++;
    return index++;
}

function addImageToMap(file, index) {
    const previewElement = createPreviewElement(file, index);
    previewContainer.appendChild(previewElement);

    // Сохраняем в Map
    fileMap.set(index, {

        file: file,
        element: previewElement,
        objectURL: previewElement.querySelector('img').src
    });
    updateFileCount()
}

function createPreviewElement(file, index) {
    const container = document.createElement("div");
    container.className = "preview-container";
    container.dataset.index = index;

    const img = document.createElement("img");
    const objectURL = URL.createObjectURL(file);
    img.src = objectURL;

    const deleteIcon = document.createElement("div");
    deleteIcon.className = "delete-icon";
    deleteIcon.innerHTML = "🗑";

    deleteIcon.addEventListener("click", (e) => {
        e.stopPropagation();
        removeImage(index);
    });

    // Обработчик клика для кадрирования
    img.addEventListener("click", (e) => {
        e.stopPropagation();
        currentCropIndex = index;
        startCropper(file);
        console.log("Кадрирование")
    });

    container.append(img, deleteIcon);
    console.log("Превью")
    return container;
}

function removeImage(img_index) {
    if (!fileMap.has(img_index)) return;

    const { element, objectURL } = fileMap.get(img_index);
    // Освобождаем память
    if (objectURL) URL.revokeObjectURL(objectURL);

    // 1. Удаляем из DOM
    element.remove();

    // 2. Освобождаем память
//    URL.revokeObjectURL(objectURL);

    // 3. Удаляем из Map
    fileMap.delete(img_index);
    updateFileCount()
}

// Для получения всех файлов (например, перед отправкой формы)
function getAllFiles() {
    return Array.from(fileMap.values()).map(item => item.file);
}

// Кадрирование изображения
function startCropper(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        cropImage.src = e.target.result;
        cropModal.show();

        if (cropper) cropper.destroy();

        cropper = new Cropper(cropImage, {
//            aspectRatio: 16/9 // для главных фото (горизонтальные)
            aspectRatio: 4/3,  // для стандартных фото
//            aspectRatio: 1    // для миниатюр
            viewMode: 1,
            autoCropArea: 1,
            responsive: true,
            movable: true,
            zoomable: true,
            rotatable: false,
        });
    };
    reader.readAsDataURL(file);
}

// Обработчик подтверждения кадрирования
document.getElementById("crop-confirm").addEventListener("click", async function () {
    if (!cropper) return;
    try {
        const oldData = fileMap.get(currentCropIndex);
                if (!oldData) {
            console.error("Нет данных для текущего индекса кадрирования");
            return;
        }
    cropper.getCroppedCanvas({ width: 1200, height: 900 }).toBlob(async (blob) => {
     try {
        // 1. Создаем новый файл из обрезанного изображения
        const croppedFile = new File([blob], `cropped_${Date.now()}.jpg`, {
            type: "image/jpeg"
        });

        // 2. Сжимаем изображение
        const resized = await resizeImage(croppedFile, 1024, 1024, 0.75);

                // 3. Удаляем старый элемент из DOM перед созданием нового
                if (oldData && oldData.element && oldData.element.parentNode) {
                    oldData.element.remove(); // Удаляем DOM-элемент
                    URL.revokeObjectURL(oldData.objectURL); // Освобождаем память
                }

        // 3. Полностью воссоздаем элемент превью (как при первоначальной загрузке)
        const newPreview = createPreviewElement(resized, currentCropIndex);

//        //4. Удаляем старый элемент превью
//        const oldData = fileMap.get(currentCropIndex);
//        if (oldData && oldData.element) {
//            URL.revokeObjectURL(oldData.objectURL);
//        }

        // 5. Обновляем данные в filesMap
        const objectURL = URL.createObjectURL(resized);
        fileMap.set(currentCropIndex, {
                    file: resized,
                    element: newPreview,
                    objectURL: objectURL
                });


        // 6. Добавляем новый элемент в DOM
        previewContainer.appendChild(newPreview);

        // 7. Закрываем модальное окно и чистим ресурсы
        cropModal.hide();
        cropper.destroy();
        cropper = null;
            } catch (e) {
                console.error("Ошибка при обработке обрезанного изображения", e);
            }
    }, "image/jpeg", 0.9);
       } catch (e) {
        console.error("Ошибка при кадрировании", e);
    }

    updateFileCount()
});

// Функция сжатия изображения (без изменений)
function resizeImage(file, maxWidth, maxHeight, quality) {
    // Возвращаем Promise для асинхронной работы
    return new Promise((resolve, reject) => {
        try {
            // 1. Создаем FileReader для чтения файла
            const reader = new FileReader();
            reader.onerror = () => reject(new Error("Ошибка чтения файла"));
            // 2. Настраиваем обработчик успешного чтения файла
            reader.onload = (event) => {
                try {
                    // 3. Создаем новый объект Image для работы с изображением
                    const img = new Image();
                    img.onerror = () => reject(new Error("Ошибка загрузки изображения"));
                    // 4. Ожидаем загрузки изображения в память
                    img.onload = () => {
                        try {
                            // 5. Создаем canvas для манипуляций с изображением
                            const canvas = document.createElement("canvas");

                            // 6. Получаем оригинальные размеры изображения
                            let width = img.width;
                            let height = img.height;

                            // 7. Масштабируем изображение с сохранением пропорций:
                            //    Если ширина больше высоты и превышает maxWidth
                            if (width > height && width > maxWidth) {
                                // 8. Вычисляем новую высоту пропорционально
                                height *= maxWidth / width;
                                width = maxWidth;
                            }
                            //    Иначе если высота превышает maxHeight
                            else if (height > maxHeight) {
                                // 9. Вычисляем новую ширину пропорционально
                                width *= maxHeight / height;
                                height = maxHeight;
                            }

                            // 10. Устанавливаем новые размеры canvas
                            canvas.width = width;
                            canvas.height = height;
                            // 11. Получаем контекст для рисования на canvas
                            const ctx = canvas.getContext("2d");
                            // 12. Рисуем изображение с новыми размерами
                            ctx.drawImage(img, 0, 0, width, height);
                            // 13. Определяем MIME-тип на основе исходного файла
                            const mimeType = file.type === "image/png" ? "image/png" : "image/jpeg";
                            // 14. Конвертируем canvas в Blob (бинарные данные изображения)
                            canvas.toBlob(blob => {
                                // 15. Генерируем уникальное имя файла с timestamp
                                const newName = `img_${Date.now()}` + (mimeType === "image/png" ? ".png" : ".jpg");
                                // 16. Создаем новый File объект из Blob
                                const resized = new File([blob], newName, { type: mimeType });
                                // 17. Возвращаем результат через Promise
                                resolve(resized);
                            }, mimeType, quality); // Указываем тип и качество
                        } catch (e) {
                            reject(e);
                        }
                    };
                    // 18. Загружаем данные изображения (сработает onload)
                    img.src = event.target.result;
                } catch (e) {
                    reject(e);
                }
            }
            // 19. Начинаем чтение файла как Data URL (base64)
            reader.readAsDataURL(file);
        } catch (e) {
            reject(e);
        }
    })
}

function updateFileCount() {
    const countText = fileMap.size ? `Выбрано: ${fileMap.size} файл(ов)` : 'Файлы не выбраны';
    document.getElementById("file-count").textContent = countText;
}

cropModal._element.addEventListener('hidden.bs.modal', function () {
    if (cropper) {
        cropper.destroy();
        cropper = null;
    }
});

// Обработчик отправки формы
adForm.addEventListener('submit', async function(e) {
    e.preventDefault();

    // Показываем индикатор загрузки
    document.getElementById('upload-indicator').style.display = 'block';

    try {
        // Создаем DataTransfer с текущими файлами
        const dataTransfer = new DataTransfer();
        fileMap.forEach(data => dataTransfer.items.add(data.file));

        // Заменяем файлы в input
        inputElement.files = dataTransfer.files;

        // Отправляем форму стандартным способом
        adForm.submit();
    } catch (error) {
        console.error('Ошибка отправки:', error);
        alert('Произошла ошибка при отправке формы');
        document.getElementById('upload-indicator').style.display = 'none';
    }
});

});