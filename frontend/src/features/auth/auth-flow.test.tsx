import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { HttpResponse, http } from 'msw'
import { beforeEach, describe, expect, it } from 'vitest'

import { AppProviders } from '../../app/providers.tsx'
import { queryClient } from '../../app/query-client.ts'
import { router } from '../../app/router.tsx'
import { getAccessToken, setAccessToken } from '../../auth/token-store.ts'
import { server } from '../../test/server.ts'

describe('authentication flow', () => {
  beforeEach(async () => {
    setAccessToken(null)
    queryClient.clear()
    await router.navigate('/')
  })

  it('redirects unauthenticated users to login', async () => {
    await router.navigate('/account')

    render(<AppProviders />)

    expect(
      await screen.findByRole('heading', { name: '登录' }),
    ).toBeInTheDocument()
  })

  it('signs in and sends the access token to protected APIs', async () => {
    server.use(
      http.post('*/api/v1/login/access-token', async ({ request }) => {
        expect(request.headers.get('X-Client-Type')).toBe('web')
        const body = await request.formData()
        expect(body.get('username')).toBe('testuser')
        return HttpResponse.json({
          access_token: 'valid-access-token',
          refresh_token: null,
          token_type: 'bearer',
          expires_in: 1800,
        })
      }),
      http.get('*/api/v1/users/me', ({ request }) => {
        expect(request.headers.get('Authorization')).toBe(
          'Bearer valid-access-token',
        )
        return HttpResponse.json({
          id: 1,
          email: 'test@example.com',
          username: 'testuser',
          display_name: 'Test User',
          avatar_url: null,
          email_verified_at: null,
          is_active: true,
          is_superuser: false,
          last_login_at: null,
          created_at: '2026-01-01T00:00:00',
          updated_at: '2026-01-01T00:00:00',
        })
      }),
    )
    await router.navigate('/login')
    const user = userEvent.setup()
    render(<AppProviders />)

    await user.type(screen.getByLabelText('用户名或邮箱'), 'testuser')
    await user.type(screen.getByLabelText('密码'), 'Test123456')
    await user.click(screen.getByRole('button', { name: '登录' }))

    expect(
      await screen.findByRole('heading', { name: 'Test User' }),
    ).toBeInTheDocument()
    expect(screen.getByText('test@example.com')).toBeInTheDocument()
  })

  it('clears authentication and returns to login after a 401', async () => {
    server.use(
      http.get('*/api/v1/users/me', () =>
        HttpResponse.json(
          {
            code: 'INVALID_ACCESS_TOKEN',
            message: '无法验证凭据',
            details: null,
          },
          { status: 401 },
        ),
      ),
    )
    setAccessToken('expired-access-token')
    await router.navigate('/account')

    render(<AppProviders />)

    expect(
      await screen.findByRole('heading', { name: '登录' }),
    ).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })
})
