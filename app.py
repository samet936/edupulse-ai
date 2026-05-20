import requests
import math
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class EduPulseMasterEngine:
    def __init__(self, data):
        self.data = data
        self.performance_score = 0

    def validate_biological_limits(self):
        """Gerçekçilik Kontrolü: Zaman ve biyoloji yasalarına uygunluk."""
        try:
            study = float(self.data.get('studytime', 0))
            sleep = float(self.data.get('sleep_hours', 0))
            social = float(self.data.get('social_media', 0))
            if (study + sleep + social + 3) > 24:
                return False, "Zaman Paradoksu: Girdiğiniz saatlerin toplamı bir günü aşıyor (Yemek/Hijyen dahil değil)."
            if sleep < 3:
                return False, "Kritik Uyku Eksikliği: Biyolojik olarak bu veriyle analiz yapılamaz."
            if float(self.data.get('G1', 0)) > 100 or float(self.data.get('G2', 0)) > 100:
                return False, "Not Hatası: Sınav notları 100'den büyük olamaz."
            return True, ""
        except:
            return False, "Veri formatı geçersiz."

    def calculate_performance_score(self):
        """V4+ Gelişmiş Formül: Yaş Çarpanı ve Kaggle Trendleri Dahil."""
        d = self.data
        
        # 1. Akademik Temel (%35) - Gelişim Trendi
        g1, g2 = float(d['G1']), float(d['G2'])
        trend = (g2 - g1) * 0.2
        academic_base = ((g1 * 0.4) + (g2 * 0.6) + trend) * 0.35

        # 2. Çalışma Verimi (%25) - Gaussian Curve (Optimal: 6 Saat)
        study_h = float(d['studytime'])
        efficiency = 25 * math.exp(-(pow(study_h - 6, 2)) / 32)
        if study_h > 12: efficiency -= (study_h - 12) * 3 # Tükenmişlik Cezası

        # 3. Biyolojik Denge (%15) - Uyku ve Sosyal Medya
        sleep_h = float(d['sleep_hours'])
        sm_h = float(d['social_media'])
        sleep_score = 10 * math.exp(-(pow(sleep_h - 7.5, 2)) / 8)
        sm_penalty = sm_h * 2.5
        lifestyle_base = (sleep_score - sm_penalty + 15)

        # 4. Mental Durum (%25) - Psikolojik Etki
        mot, anx = float(d['motivation']), float(d['anxiety'])
        fatigue, energy = float(d['mental_fatigue']), float(d['daily_energy_trend'])
        
        anx_impact = anx * 1.5
        if anx >= 7: anx_impact += pow(anx - 6, 2.5) 
        
        mental_base = (mot * 2) + (energy * 1.5) - (fatigue * 2) - anx_impact
        mental_normalized = max(-10, min(25, mental_base))

        # --- YAŞ ÇARPANI (Biyolojik Verimlilik Katmanı) ---
        age = float(d.get('age', 20))
        if 18 <= age <= 24: age_mult = 1.08
        elif 25 <= age <= 35: age_mult = 1.03
        elif age < 18: age_mult = 1.00
        else: age_mult = 0.94

        # Final Normalization (Sigmoid)
        raw_total = academic_base + efficiency + (lifestyle_base * 0.15 * 10) + mental_normalized
        final = 100 / (1 + math.exp(-(raw_total - 50) / 15))
        
        self.performance_score = round(max(5, min(99, final * age_mult)), 1)
        return self.performance_score

    def build_strategy_logic(self):
        """Strateji Motoru: Kişiselleştirilmiş Tavsiyeler."""
        d = self.data
        days = int(d['exam_days_left'])
        score = self.performance_score
        
        if days > 60: mode, phase = "🛡️ Learning Phase", "Geniş zamanlı konu inşası."
        elif days > 30: mode, phase = "⚙️ Optimization", "Hız ve pratik odaklı süreç."
        elif days > 15: mode, phase = "🚀 Acceleration", "Deneme ağırlıklı yüksek tempo."
        else: mode, phase = "💀 Survival Mode", "Sadece en çok soru çıkan noktalara odak."

        if score >= 85: 
            status = "Elite Performans: Zirvedesin!"
            problem = f"{d['zayif_konu']} üzerindeki ufak pürüzler seni kusursuzluktan alıkoyuyor."
            strategy = f"{d['guclu_ders']} netlerini koru, vaktini {d['zayif_ders']} branşına kaydır."
        elif score >= 70:
            status = "Yükseliş Trendi: Sistem verimli çalışıyor."
            problem = "Mental yorgunluk ve rutin kaybı riski mevcut."
            strategy = f"Deneme sayısını artır, {d['zayif_konu']} için her sabah 30 dk ayır."
        elif score >= 50:
            status = "Denge Arayışı: Potansiyel var ama disiplin eksik."
            problem = f"{d['zayif_ders']} dersindeki önyargı gelişimini engelliyor."
            strategy = f"Önce {d['guclu_ders']} ile ısın, sonra en zorlandığın {d['zayif_konu']} çalış."
        else:
            status = "Acil Müdahale: Sistem çökme riski taşıyor."
            problem = "Düşük uyku ve yüksek kaygı bilişsel kapasiteyi kilitliyor."
            strategy = "Uykuyu 7 saate sabitle and sadece son 5 yılın sorularına odaklan."

        return {
            "mode": mode, "phase_desc": phase, "status_msg": status,
            "problem_msg": problem
