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
        # SSML 직접 입력 또는 JSON으로 속성 전달
        if 'ssml' in request_json:
            ssml = request_json['ssml']
        elif 'segments' in request_json:
            # JSON segments를 SSML로 변환
            segments = request_json['segments']
            ssml = '<speak>'
            for segment in segments:
                text = segment.get('text', '')
                rate = segment.get('rate', '1.0')
                emphasis = segment.get('emphasis', 'none')
                break_time = segment.get('break', '0ms')
                ssml += f'<prosody rate="{rate}">'
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
        voice_name = request_json.get('voice', 'ko-KR-Wavenet-A')
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name=voice_name
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        headers['Content-Type'] = 'audio/mp3'
        return (response.audio_content, 200, headers)
    except Exception as e:
        return (f'에러: {str(e)}', 500, headers)