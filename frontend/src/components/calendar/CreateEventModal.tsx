"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useCalendarStore } from "@/store/calendarStore";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

const schema = z
  .object({
    title: z.string().min(1, "Title is required"),
    start_time: z.string().min(1, "Start time is required"),
    end_time: z.string().min(1, "End time is required")
  })
  .refine((v) => new Date(v.end_time) > new Date(v.start_time), {
    message: "End time must be after start time",
    path: ["end_time"]
  });

type FormValues = z.infer<typeof schema>;

export function CreateEventModal() {
  const { isCreateModalOpen, closeCreateModal, createEvent } = useCalendarStore();
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting }
  } = useForm<FormValues>({ resolver: zodResolver(schema) });

  async function onSubmit(values: FormValues) {
    try {
      await createEvent(values);
      toast.success("Event created");
      reset();
    } catch {
      toast.error("Couldn't create the event");
    }
  }

  return (
    <Modal open={isCreateModalOpen} onClose={closeCreateModal} title="New event">
      <form className="space-y-4" onSubmit={handleSubmit(onSubmit)}>
        <div>
          <label className="mb-1 block text-sm font-medium">Title</label>
          <Input {...register("title")} placeholder="Team sync" />
          {errors.title && <p className="mt-1 text-xs text-danger">{errors.title.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Start</label>
          <Input type="datetime-local" {...register("start_time")} />
          {errors.start_time && (
            <p className="mt-1 text-xs text-danger">{errors.start_time.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">End</label>
          <Input type="datetime-local" {...register("end_time")} />
          {errors.end_time && (
            <p className="mt-1 text-xs text-danger">{errors.end_time.message}</p>
          )}
        </div>
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Creating…" : "Create event"}
        </Button>
      </form>
    </Modal>
  );
}
