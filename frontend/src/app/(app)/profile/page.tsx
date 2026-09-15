import { AppShell } from "@/components/layout/AppShell";
import { ProfileForm } from "@/components/profile/ProfileForm";

export default function ProfilePage() {
  return (
    <AppShell rightPanel={false}>
      <div className="mx-auto w-full max-w-2xl space-y-6 p-6">
        <h1 className="font-display text-2xl font-black">Profile</h1>
        <ProfileForm />
      </div>
    </AppShell>
  );
}