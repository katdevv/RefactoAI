import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Task {
  id: number;
  topic: string;
  name: string;
}
interface TasksResponse {
  tasks: Task[];
}

type Grouped = { topic: string; tasks: { name: string; id: number }[] };

const API_URL =
  (import.meta as any).env?.VITE_API_URL || "http://127.0.0.1:8000";

export const grouper = async (): Promise<Grouped[]> => {
  try {
    console.log("API:", API_URL);
    const res = await fetch(`${API_URL}/tasks`, {
      headers: { "Accept": "application/json" },
    });

    const contentType = res.headers.get("content-type") || "";
    const text = await res.text();

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${text.slice(0, 200)}`);
    }
    if (!contentType.includes("application/json")) {
      throw new SyntaxError(
        `Expected JSON but got '${contentType}'. Body: ${text.slice(0, 200)}`
      );
    }

    const data: TasksResponse = JSON.parse(text);

    const grouped = data.tasks.reduce((acc: Grouped[], task) => {
      let group = acc.find((g) => g.topic === task.topic);
      if (!group) {
        group = { topic: task.topic, tasks: [] };
        acc.push(group);
      }
      group.tasks.push({ name: task.name, id: task.id });
      return acc;
    }, []);

    return grouped;
  } catch (err) {
    console.error(err);
    throw new Error("Something Went Wrong While Grouping Data");
  }
};
