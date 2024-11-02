# Testing file upload
echo "Testing file upload..."
curl -X 'POST' \
'http://localhost:8000/uploadfile/' \
-H 'accept: application/json' \
-H 'Content-Type: multipart/form-data' \
-F 'file=@obama.txt;type=text/plain'
echo ""
echo ""

# Testing the root endpoint
echo "Testing the root endpoint..."
curl -X 'GET' 'http://localhost:8000/' -H 'accept: application/json'
echo ""
echo ""

# Wait for 30 seconds before testing question answering
echo "Waiting for 30 seconds before testing question answering..."
sleep 30

# Testing question answering
echo "Testing question answering..."
curl -X 'POST' \
'http://localhost:8000/ask/' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{"document_id": 1, "question": "When was Barack Obama elected for the second time ?"}'
echo ""
echo ""

# Testing similar chunk retrieval
echo "Testing similar chunk retrieval..."
curl -X 'POST' \
'http://localhost:8000/find-similar-chunks/1' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{"question": "Who is Barack Obama wife and when did they meet ?"}'
echo ""
echo ""

# echo "Testing the root endpoint..."
# printf "\n"
# curl http://127.0.0.1:8000

# printf "\n"
# echo "Testing the root endpoint with Path Param ..."
# printf "\n"
# curl http://127.0.0.1:8000/greet/Vaibhavi

# printf "\n"
# echo "Testing file upload..."
# printf "\n"
# curl -X 'POST' 'http://127.0.0.1:8000/uploadfile/' -F 'file=@requirements.txt'

# printf "\n"
# echo "Testing file upload - Error case..."
# printf "\n"
# curl -X 'POST' 'http://127.0.0.1:8000/uploadfile/' -F 'file=@dummy.png'


# printf "\n"
# echo "Testing the ask question endpoint..."
# printf "\n"
# curl -X 'POST' \
# 'http://127.0.0.1:8000/ask/' \
# -H 'accept: application/json' \
# -H 'Content-Type: application/json' \
# -d '{
# "question": "Whats the capital of Sweden?"
# }'  | jq '.'
