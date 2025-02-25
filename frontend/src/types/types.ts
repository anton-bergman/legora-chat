export interface LastMessageResponse {
	sender?: string;
	text?: string;
	timestamp?: string; // ISO string
}

export interface ChatResponse {
	chatId: string;
	participants: string[];
	lastMessage?: LastMessageResponse;
}

export interface MessageResponse {
	messageId: string;
	chatId: string;
	sender: string;
	text: string;
	timestamp: string; // ISO string
}

export interface ChatMessageResponse {
	chatId: string;
	messages: MessageResponse[];
}
