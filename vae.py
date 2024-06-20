import jams
import numpy as np
import tensorflow as tf
from keras import layers, models


def load_choco_jams(jams_file):
    jam = jams.load(jams_file, validate=False)
    chords = jam.annotations.search(namespace="chord")[0]
    chord_progressions = []
    
    for chord in chords:
        value = chord.value
        chord_progressions.append(value)
    
    return chord_progressions

jams_file = "data/jams/billboard_341.jams"
chord_progressions = load_choco_jams(jams_file)



latent_dim = 2

# Encoder
def create_encoder(input_shape, latent_dim):
    inputs = layers.Input(shape=input_shape)
    x = layers.Flatten()(inputs)
    x = layers.Dense(128, activation='relu')(x)
    z_mean = layers.Dense(latent_dim)(x)
    z_log_var = layers.Dense(latent_dim)(x)
    encoder = models.Model(inputs, [z_mean, z_log_var])
    return encoder

# Decoder
def create_decoder(latent_dim, output_shape):
    latent_inputs = layers.Input(shape=(latent_dim,))
    x = layers.Dense(128, activation='relu')(latent_inputs)
    x = layers.Dense(np.prod(output_shape), activation='sigmoid')(x)
    outputs = layers.Reshape(output_shape)(x)
    decoder = models.Model(latent_inputs, outputs)
    return decoder

# Sampling layer
class Sampling(layers.Layer):
    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = tf.shape(z_mean)[0]
        dim = tf.shape(z_mean)[1]
        epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

# VAE Model
def create_vae(input_shape, latent_dim):
    encoder = create_encoder(input_shape, latent_dim)
    decoder = create_decoder(latent_dim, input_shape)
    
    inputs = layers.Input(shape=input_shape)
    z_mean, z_log_var = encoder(inputs)
    z = Sampling()([z_mean, z_log_var])
    outputs = decoder(z)
    
    vae = models.Model(inputs, outputs)
    
    # loss
    reconstruction_loss = tf.keras.losses.binary_crossentropy(inputs, outputs)
    reconstruction_loss *= np.prod(input_shape)
    kl_loss = 1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var)
    kl_loss = tf.reduce_mean(kl_loss, axis=-1)
    kl_loss *= -0.5
    vae_loss = tf.reduce_mean(reconstruction_loss + kl_loss)
    
    vae.add_loss(vae_loss)
    vae.compile(optimizer='adam')
    
    return vae, encoder, decoder

# remove 'N' chords 
def clean_chords(chord_progressions):
    chord_progressions = [chord for chord in chord_progressions if chord != "N"]  
    return chord_progressions
chord_progressions = clean_chords(chord_progressions)

# Define input shape based on chord progression data
input_shape = (len(chord_progressions), 1)  # e.g. (87, 1)
vae, encoder, decoder = create_vae(input_shape, latent_dim)

print("############ Encoder summary ############")
encoder.summary()
print("############ Decoder summary ############")
decoder.summary()
print("############ VAE summary ############")
vae.summary()


# Convert data to numpy array
chord_progressions = np.array([str(ch) for ch in chord_progressions]).reshape(-1, 1)

# Normalize the data
#chord_progressions = (chord_progressions - np.min(chord_progressions)) / (np.max(chord_progressions) - np.min(chord_progressions))


# Train VAE
vae.fit(chord_progressions, chord_progressions, epochs=50, batch_size=32, verbose=2)

# Generate new chords by sampling from the latent space
def generate_chords(decoder, num_samples=10):
    z_samples = np.random.normal(size=(num_samples, latent_dim))
    generated_chords = decoder.predict(z_samples)
    return generated_chords

new_chords = generate_chords(decoder, num_samples=10)
print(new_chords)
