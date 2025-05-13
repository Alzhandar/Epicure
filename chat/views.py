import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatSerializer
from .models import ChatMessage

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


model = genai.GenerativeModel("gemini-1.5-flash")

class ChatAPIView(APIView):
    def post(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.validated_data["message"]
            user = request.user if request.user.is_authenticated else None

            try:
                ChatMessage.objects.create(user=user, role="user", content=message)

                response = model.generate_content(message)
                reply = response.text

                ChatMessage.objects.create(user=user, role="bot", content=reply)

                return Response({"response": reply})

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
