import { RegisterForm } from "@/features/auth/sign-up/ui/register-form";
import { AuthPageShell } from "@/widgets/auth-shell/ui/auth-page-shell";

export function RegisterPage() {
  return (
    <AuthPageShell
      title="Регистрация"
      description="Создайте отдельную учетную запись для работы с операционной панелью лаборатории."
    >
      <RegisterForm />
    </AuthPageShell>
  );
}
