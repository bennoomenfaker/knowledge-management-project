# Refresh et run frontend
fuser -k 3000/tcp 2>/dev/null; rm -rf /home/himawari/workSpace/knowledgeManagementProject/frontend/.next
cd /home/himawari/workSpace/knowledgeManagementProject/frontend && npm run dev