import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Plus } from 'lucide-react';
import { CreateSessionFormSchema, type CreateSessionFormValues } from '../lib/schemas';
import { useCreateSession } from '../hooks/useSessions';
import { useCurrentSession } from '../contexts/SessionContext';

type Props = {
  onSuccess?: () => void;
};

export function CreateSessionForm({ onSuccess }: Props) {
  const createSession = useCreateSession();
  const { setCurrentSessionId } = useCurrentSession();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CreateSessionFormValues>({
    resolver: zodResolver(CreateSessionFormSchema),
    defaultValues: { name: '', external_link: '' },
  });

  const onSubmit = handleSubmit((data) => {
    createSession.mutate(
      {
        name: data.name?.trim() || null,
        external_link: data.external_link?.trim() || null,
      },
      {
        onSuccess: (session) => {
          setCurrentSessionId(session.id);
          reset();
          onSuccess?.();
        },
      }
    );
  });

  return (
    <form onSubmit={onSubmit} className="space-y-2">
      <div>
        <label htmlFor="create-session-name" className="label text-xs">
          Name (optional)
        </label>
        <input
          id="create-session-name"
          type="text"
          className="input input-bordered input-sm w-full"
          placeholder="e.g. Incident #123"
          aria-invalid={!!errors.name}
          {...register('name')}
        />
        {errors.name && (
          <p className="text-error text-xs mt-0.5" role="alert">
            {errors.name.message}
          </p>
        )}
      </div>
      <div>
        <label htmlFor="create-session-link" className="label text-xs">
          External link (optional)
        </label>
        <input
          id="create-session-link"
          type="text"
          className="input input-bordered input-sm w-full"
          placeholder="e.g. https://..."
          aria-invalid={!!errors.external_link}
          {...register('external_link')}
        />
        {errors.external_link && (
          <p className="text-error text-xs mt-0.5" role="alert">
            {errors.external_link.message}
          </p>
        )}
      </div>
      <button
        type="submit"
        className="btn btn-primary btn-sm w-full flex items-center justify-center gap-2"
        disabled={createSession.isPending}
        aria-busy={createSession.isPending}
        aria-label="Create new session"
      >
        {createSession.isPending ? (
          <span className="loading loading-spinner loading-sm" aria-hidden />
        ) : (
          <Plus size={18} aria-hidden />
        )}
        {createSession.isPending ? 'Creating…' : 'Create session'}
      </button>
      {createSession.isError && (
        <p className="text-error text-xs" role="alert">
          {createSession.error?.message}
        </p>
      )}
    </form>
  );
}
