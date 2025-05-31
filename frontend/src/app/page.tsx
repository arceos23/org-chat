import { ChatInterface } from "@/components/chat-interface";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 md:p-24">
      <h1 className="text-3xl font-bold mb-8">OrgChat</h1>
      <div className="w-full max-w-2xl">
        <ChatInterface apiEndpoint="http://localhost:8000/chat" />
      </div>
    </main>
  );
}
