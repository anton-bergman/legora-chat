import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  ChatResponse,
  MessageResponse,
  ChatMessageResponse,
} from "../types/types";
import axios from "axios";
import { Socket } from "socket.io-client";

function Home() {
  const { logout, token, user, socket } = useAuth();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sendMessageText, setSendMessageText] = useState<string>("");
  const [chats, setChats] = useState<ChatResponse[]>([]);
  const [selectedChat, setSelectedChat] = useState<ChatResponse | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);

  const handleLogout = (): void => {
    logout();
    navigate("/");
  };

  const fetchUserChats = async (token: string): Promise<void> => {
    try {
      const response = await axios.get("http://127.0.0.1:5000/api/chats", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      const newChat = response.data as ChatResponse[];
      setChats(newChat);
    } catch (error) {
      console.error("Error fetching chats:", error);
      throw error;
    }
  };

  const fetchChatMessages = async (
    chat: ChatResponse,
    token: string,
    socket: Socket
  ): Promise<void> => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:5000/api/chats/${chat.chatId}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const chatMessageResponse = response.data as ChatMessageResponse;
      const messageList = chatMessageResponse.messages;
      setMessages(messageList);
      socket.emit("join_chat", chat);
    } catch (error) {
      console.error("Error fetching chat messages:", error);
      throw error;
    }
  };

  useEffect(() => {
    if (token) {
      fetchUserChats(token);
    }
  }, [token, socket]);

  useEffect(() => {
    if (selectedChat && token && socket) {
      fetchChatMessages(selectedChat, token, socket);
    }
  }, [selectedChat, token, socket]);

  useEffect(() => {
    if (!socket) return;

    socket.on("new_chat", (newChat) => {
      setChats((prevChats) => [newChat, ...prevChats]);
    });

    socket.on("new_message", (message) => {
      setMessages((prevMessages) => [...prevMessages, message]);
    });

    socket.on("join_chat", (chat) => {
      setChats((prevChats) => [chat, ...prevChats]);
    });

    socket.on("error", (error) => {
      console.error(error);
    });

    return () => {
      socket.off("new_chat");
      socket.off("new_message");
      socket.off("join_chat");
      socket.off("error");
    };
  }, [socket]);

  const handleChatClick = (chat: ChatResponse): void => {
    if (selectedChat?.chatId === chat?.chatId) {
      return;
    }
    setSelectedChat(chat);
  };

  const handleSendMessage = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!sendMessageText.trim() || !selectedChat || !token || !socket) return;

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/api/messages",
        {
          chat_id: selectedChat.chatId,
          text: sendMessageText,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const newMessage = response.data as MessageResponse;
      socket.emit("send_message", newMessage);
      setSendMessageText("");
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  const handleCreateChatSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (!searchTerm.trim() || !token || !socket) return;
    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/api/chats",
        {
          participant_username: searchTerm,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const newChat = response.data as ChatResponse;
      socket.emit("new_chat", newChat);
      setChats((prevChats) => [newChat, ...prevChats]);
      setSearchTerm("");
    } catch (error) {
      console.error("Error creating new chat:", error);
      alert("Failed to create a new chat.");
    }
  };

  const getParticipantsDisplay = (
    participants: string[],
    username: string
  ): string => {
    // Filter out the given username from the participants list
    const filteredParticipants = participants.filter(
      (participant) => participant !== username
    );
    return filteredParticipants.join(", ");
  };

  return (
    <div className="flex flex-col items-center gap-8">
      {/* ----- Start a Chat ----- */}
      <form>
        <div className="flex flex-col gap-1">
          <label>Start a chat with a user</label>
          <div className="flex gap-5">
            <input
              className="flex border border-white rounded p-1 w-80"
              type="username"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Enter a username"
            />
            <button type="submit" onClick={handleCreateChatSubmit}>
              Start chat
            </button>
          </div>
        </div>
      </form>

      <div className="flex gap-5">
        {/* ----- Open Chats ----- */}
        <ol className="flex flex-col gap-3 p-2 w-90 h-150 border border-white rounded-md overflow-auto">
          {chats.map((chat, i) => (
            <li
              className={`font-semibold border border-white rounded p-2 min-h-15 cursor-pointer hover:bg-gray-700 ${
                selectedChat?.chatId === chat.chatId ? "bg-gray-900" : ""
              }`}
              key={i}
              onClick={() => handleChatClick(chat)}
            >
              {getParticipantsDisplay(chat.participants, user ?? "")}
            </li>
          ))}
        </ol>

        {/* ----- Chat view ----- */}
        <div className="flex flex-col w-90 h-150 border border-white rounded-md">
          <ol className="flex flex-col gap-3 p-2 h-full overflow-auto">
            {messages.map((message, i) => {
              return (
                <li
                  className={`flex ${
                    message.sender === user ? "justify-end" : "justify-start"
                  }`}
                  key={i}
                >
                  <div className="max-w-[55%] border border-white rounded-xl p-2">
                    {message.text}
                  </div>
                </li>
              );
            })}
          </ol>

          {/* ----- Send message ----- */}
          <form>
            <div className="flex gap-2 p-2">
              <input
                className="border border-white rounded p-1 w-full"
                type="text"
                value={sendMessageText}
                onChange={(e) => setSendMessageText(e.target.value)}
                placeholder="Send message"
              />
              <button type="submit" onClick={handleSendMessage}>
                Send
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* ----- Logout ----- */}
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default Home;
