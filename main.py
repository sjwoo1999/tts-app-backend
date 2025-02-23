from google.cloud import texttospeech
import functions_framework
import json

@functions_framework.http
def generate_tts(request):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST',
        'Access-Control-Allow-Headers': 'Content-Type'
    }
    if request.method == 'OPTIONS':
        return ('', 204, headers)

    request_json = request.get_json(silent=True)
    if not request_json:
        return ('요청 데이터 필요', 400, headers)

    try:
        if 'ssml' in request_json:
            ssml = request_json['ssml']
        elif 'segments' in request_json:
            segments = request_json['segments']
            ssml = '<speak>'
            for segment in segments:
                text = segment.get('text', '')
                rate = segment.get('rate', '1.0')  # 기본값 고정, 0.25~4.0 범위 제한
                emphasis = segment.get('emphasis', 'none')
                break_time = segment.get('break', '0ms')
                # 피치 기본값 0.0, 과도한 설정 방지
                pitch = segment.get('pitch', '0.0')
                try:
                    pitch_value = float(pitch)  # 부동소수점 변환
                    if pitch_value < -10.0 or pitch_value > 10.0:  # 범위 제한
                        pitch_value = 0.0  # 과도한 값은 기본값으로
                except (ValueError, TypeError):
                    pitch_value = 0.0  # 잘못된 값은 기본값으로
                ssml += f'<prosody rate="{rate}" pitch="{pitch_value}">'
                if emphasis != 'none':
                    ssml += f'<emphasis level="{emphasis}">{text}</emphasis>'
                else:
                    ssml += text
                ssml += f'</prosody><break time="{break_time}"/>'
            ssml += '</speak>'
        else:
            return ('SSML 또는 segments 필요', 400, headers)

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
        
        language_code = request_json.get('language', 'ko-KR')
        voice_name = request_json.get('voice', 'ko-KR-Wavenet-A')
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name
        )
        # 자연스러운 목소리 기본 설정
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=0.0,  # 기본 피치, 자연스러움 유지
            speaking_rate=1.0  # 기본 속도, 자연스러움 유지
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        headers['Content-Type'] = 'audio/mp3'
        return (response.audio_content, 200, headers)
    except Exception as e:
        return (f'에러: {str(e)}', 500, headers)