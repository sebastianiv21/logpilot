import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Save } from 'lucide-react';
import { EditSessionFormSchema, type EditSessionFormValues } from '../lib/schemas';
import type { Session } from '../lib/schemas';
import { usePatchSession } from '../hooks/useSessions';

type Props = {
  session: Session;
  onSuccess?: () => void;
  onCancel?: () => void;
};

export function EditSessionForm({ session, onSuccess, onCancel }: Props) {
  const patchSession = usePatchSession();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EditSessionFormValues>({
    resolver: zodResolver(EditSessionFormSchema),
    defaultValues: {
      name: session.name ?? '',
      external_link: session.external_link ?? '',
      is_pinned: session.is_pinned,
    },
  });

  const onSubmit = handleSubmit((data) => {
    patchSession.mutate(
      {
        id: session.id,
        body: {
          name: data.name?.trim() || null,
          external_link: data.external_link?.trim() || null,
          is_pinned: !!data.is_pinned,
        },
      },
      { onSuccess: () => onSuccess?.() }
    );
  });

  return (
    <form onSubmit={onSubmit} className="space-y-2">
      <div>
        <label htmlFor="edit-session-name" className="label text-xs">
          Name (optional)
        </label>
        <input
          id="edit-session-name"
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
        <label htmlFor="edit-session-link" className="label text-xs">
          External link (optional)
        </label>
        <input
          id="edit-session-link"
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
      <label className="label cursor-pointer justify-start gap-3 rounded-lg border border-base-300 px-3 py-2">
        <input
          type="checkbox"
          className="checkbox checkbox-sm"
          {...register('is_pinned')}
        />
        <span className="text-sm">Pin this session to protect it from automatic cleanup</span>
      </label>
      <div className="flex gap-2 pt-1">
        <button
          type="submit"
          className="btn btn-primary btn-sm flex-1 flex items-center justify-center gap-2"
          disabled={patchSession.isPending}
          aria-busy={patchSession.isPending}
          aria-label="Save session changes"
        >
          {patchSession.isPending ? (
            <span className="loading loading-spinner loading-sm" aria-hidden />
          ) : (
            <Save size={18} aria-hidden />
          )}
          {patchSession.isPending ? 'Saving…' : 'Save'}
        </button>
        {onCancel && (
          <button type="button" className="btn btn-ghost btn-sm" onClick={onCancel} aria-label="Cancel editing">
            Cancel
          </button>
        )}
      </div>
      {patchSession.isError && (
        <p className="text-error text-xs" role="alert">
          {patchSession.error?.message}
        </p>
      )}
    </form>
  );
}
