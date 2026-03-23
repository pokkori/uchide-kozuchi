import Anthropic from "@anthropic-ai/sdk";
import { NextRequest } from "next/server";

const client = new Anthropic();

export async function POST(req: NextRequest) {
  try {
    const { wish } = await req.json();

    if (!wish || typeof wish !== "string" || wish.trim().length === 0) {
      return new Response("願い事を入力してください。", { status: 400 });
    }

    const trimmedWish = wish.trim().slice(0, 200);

    const stream = client.messages.stream({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 1024,
      messages: [
        {
          role: "user",
          content: `以下の願い事を実現するための具体的なステップを5つ、番号付きリストで提案してください。各ステップは50〜80字程度で、実践的で行動可能な内容にしてください。番号は「1.」「2.」「3.」「4.」「5.」の形式で書いてください。

願い事: ${trimmedWish}`,
        },
      ],
    });

    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        try {
          for await (const chunk of stream) {
            if (
              chunk.type === "content_block_delta" &&
              chunk.delta.type === "text_delta"
            ) {
              controller.enqueue(encoder.encode(chunk.delta.text));
            }
          }
          controller.close();
        } catch (err) {
          controller.error(err);
        }
      },
    });

    return new Response(readable, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
        "Cache-Control": "no-cache",
        "X-Content-Type-Options": "nosniff",
      },
    });
  } catch {
    return new Response("エラーが発生しました。しばらくしてから再度お試しください。", {
      status: 500,
    });
  }
}
