# generate_sounds.py
# Генератор креативных аркадных звуков. Чистый Python, без внешних зависимостей.
# Версия 2.0: исправлен звук Game Over (теперь приятный "грустный тромбон")

import os
import struct
import math
import random

def write_wav(filename, samples, sample_rate=44100):
    """Сохраняет список сэмплов (-1.0..1.0) в WAV файл."""
    with open(filename, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<L', 36 + len(samples) * 2))
        f.write(b'WAVEfmt ')
        f.write(struct.pack('<LHHLLHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        f.write(b'data')
        f.write(struct.pack('<L', len(samples) * 2))
        for s in samples:
            # Нормализация и упаковка в 16-bit PCM
            val = int(max(-32768, min(32767, s * 25000)))
            f.write(struct.pack('<h', val))

def adsr(total_samples, attack_pct, decay_pct, sustain_level, release_pct):
    """Создаёт ADSR-огибающую для плавной динамики звука."""
    env = []
    for i in range(total_samples):
        t = i / total_samples
        if t < attack_pct:
            env.append(t / max(attack_pct, 0.001))
        elif t < attack_pct + decay_pct:
            env.append(1.0 - (1.0 - sustain_level) * (t - attack_pct) / max(decay_pct, 0.001))
        elif t < 1.0 - release_pct:
            env.append(sustain_level)
        else:
            env.append(sustain_level * (1.0 - (t - (1.0 - release_pct)) / max(release_pct, 0.001)))
    return env

def freq_sweep(freq_start, freq_end, length_sec, sr, wave='sine', env=None):
    """Генерирует тон с плавным изменением частоты (питч-бенд)."""
    samples = []
    total = int(length_sec * sr)
    if env is None:
        env = [1.0] * total
    for i in range(total):
        t = i / sr
        amp = env[i] if i < len(env) else 0.0
        freq = freq_start + (freq_end - freq_start) * (i / total)
        
        if wave == 'sine':
            val = math.sin(2 * math.pi * freq * t)
        elif wave == 'square':
            val = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
        elif wave == 'saw':
            val = 2.0 * (t * freq - math.floor(0.5 + t * freq))
        else:
            val = 0.0
        samples.append(val * amp)
    return samples

def mix_layers(*layers):
    """Смешивает несколько звуковых слоёв, выравнивая длину."""
    min_len = min(len(layer) for layer in layers)
    mixed = [0.0] * min_len
    for layer in layers:
        for i in range(min_len):
            mixed[i] += layer[i]
    # Нормализация, чтобы не было клиппинга
    max_val = max(abs(v) for v in mixed) if mixed else 1.0
    if max_val > 0:
        mixed = [v / max_val for v in mixed]
    return mixed

# 🔊 ЗВУК ПОЕДАНИЯ: Мягкий восходящий звон (синайная волна для приятности)
def make_eat_sound():
    sr = 44100
    length = 0.1
    env = adsr(int(length * sr), 0.05, 0.2, 0.5, 0.20)
    coin = freq_sweep(600, 1200, length, sr, 'sine', env)
    tail = freq_sweep(1400, 1800, length, sr, 'sine', env)
    return mix_layers(coin, [t * 0.4 for t in tail])

# 🎹 ЗВУК ПРОИГРЫША: "Грустный тромбон" (нисходящая ретро-мелодия)
def make_die_sound():
    sr = 44100
    
    note1_len = 0.1
    note1 = freq_sweep(400, 380, note1_len, sr, 'square', 
                       adsr(int(note1_len * sr), 0.1, 0.1, 0.8, 0.1))
    
    note2_len = 0.1
    note2 = freq_sweep(350, 300, note2_len, sr, 'square', 
                       adsr(int(note2_len * sr), 0.1, 0.1, 0.8, 0.1))
    
    note3_len = 0.4
    note3 = freq_sweep(280, 80, note3_len, sr, 'square', 
                       adsr(int(note3_len * sr), 0.1, 0.2, 0.5, 0.20))
    
    # Последовательное объединение нот
    return note1 + note2 + note3

# 🔘 ЗВУК КЛИКА: Короткий, чёткий ретро-щелчок
def make_click_sound():
    sr = 44100
    length = 0.04
    env = adsr(int(length * sr), 0.05, 0.10, 0.0, 0.35)
    tick = freq_sweep(1200, 800, length, sr, 'square', env)
    return tick

# 🚀 Генерация
if __name__ == "__main__":
    os.makedirs("sounds", exist_ok=True)
    print("🎛️ Генерация креативных звуков (V2 - Исправлен Game Over)...")
    
    write_wav("sounds/eat.wav", make_eat_sound())
    print("✅ eat.wav — Мягкий восходящий звон")
    
    write_wav("sounds/die.wav", make_die_sound())
    print("✅ die.wav — Классический 'Грустный тромбон'")
    
    write_wav("sounds/click.wav", make_click_sound())
    print("✅ click.wav — Короткий ретро-щелчок")
    
    print("🎉 Готово! Перезапусти игру, чтобы услышать разницу.")