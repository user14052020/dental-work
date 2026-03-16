import { LoginForm } from "@/features/auth/sign-in/ui/login-form";
import { AuthPageShell } from "@/widgets/auth-shell/ui/auth-page-shell";

export function LoginPage() {
  return (
    <AuthPageShell
      title="Вход в систему"
      description="Используйте корпоративную электронную почту и пароль для доступа к веб-кабинету."
    >
      <LoginForm />
    </AuthPageShell>
  );
}
