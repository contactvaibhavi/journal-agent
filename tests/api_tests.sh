echo "Testing the root endpoint..."
printf "\n"
curl http://127.0.0.1:8000

printf "\n"
echo "Testing the root endpoint with Path Param ..."
printf "\n"
curl http://127.0.0.1:8000/greet/Vaibhavi

printf "\n"
echo "Testing file upload..."
printf "\n"
curl -X 'POST' 'http://127.0.0.1:8000/uploadfile/' -F 'file=@requirements.txt'

printf "\n"
echo "Testing file upload - Error case..."
printf "\n"
curl -X 'POST' 'http://127.0.0.1:8000/uploadfile/' -F 'file=@dummy.png'


printf "\n"
echo "Testing the ask question endpoint..."
printf "\n"
curl -X 'POST' \
'http://127.0.0.1:8000/ask/' \
-H 'accept: application/json' \
-H 'Content-Type: application/json' \
-d '{
"question": "Whats the capital of Sweden?"
}'  | jq '.'
