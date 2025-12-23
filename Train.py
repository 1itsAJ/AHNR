import tensorflow

def Start(DatasetPath,ModelPath):
    
    train_dataset = tensorflow.keras.utils.image_dataset_from_directory(
        DatasetPath,
        image_size=(20,20),
        batch_size= 32,
        color_mode='grayscale',
        validation_split=0.2, 
        subset="training",    
        seed=42               
    )

    test_dataset = tensorflow.keras.utils.image_dataset_from_directory(
        DatasetPath,
        image_size=(20,20),
        batch_size= 32,
        color_mode='grayscale',
        validation_split=0.2,  
        subset="validation",   
        seed=42                
    )

    model = tensorflow.keras.models.Sequential([
        tensorflow.keras.layers.Rescaling(1./255, input_shape=(20,20,1)),
        tensorflow.keras.layers.Conv2D(32, (3,3), activation='relu', padding='same'),
        tensorflow.keras.layers.MaxPooling2D((2,2)),
        tensorflow.keras.layers.Conv2D(64, (3,3), activation='relu', padding='same'),
        tensorflow.keras.layers.MaxPooling2D((2,2)),
        tensorflow.keras.layers.Flatten(),
        tensorflow.keras.layers.Dense(128, activation='relu'),
        tensorflow.keras.layers.Dense(10, activation='softmax')
    ])

    model.compile(
        optimizer='adam', 
        loss='sparse_categorical_crossentropy', 
        metrics=['accuracy']
    )
 
    stopper = tensorflow.keras.callbacks.EarlyStopping(
        monitor='val_loss', 
        patience=5,                        
        restore_best_weights=True         
    )
    model.fit(
        train_dataset,
        epochs=100,
        validation_data=test_dataset,
        callbacks=[stopper]
    )

    model.save(ModelPath)
    print("Best model saved")