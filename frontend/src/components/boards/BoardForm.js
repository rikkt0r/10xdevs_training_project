import React from 'react';
import { Form } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';
import FormGroup from '../common/FormGroup';
import Input from '../common/Input';
import Textarea from '../common/Textarea';
import Select from '../common/Select';
import Button from '../common/Button';
import useFormValidation from '../../hooks/useFormValidation';
import { validateRequired, validateMaxLength, validateAlphanumericHyphen } from '../../utils/validationUtils';

/**
 * BoardForm component
 * Form for creating or editing a board
 */
const BoardForm = ({ initialValues = {}, onSubmit, loading = false }) => {
  const { t } = useTranslation();

  const validationRules = {
    name: (value) => validateRequired(value, t('boards.errors.nameRequired')),
    unique_name: (value) => {
      const requiredCheck = validateRequired(value, t('boards.uniqueName'));
      if (!requiredCheck.isValid) return requiredCheck;

      const alphanumericCheck = validateAlphanumericHyphen(value, t('boards.uniqueName'));
      if (!alphanumericCheck.isValid) return alphanumericCheck;

      const maxLengthCheck = validateMaxLength(value, 255, t('boards.uniqueName'));
      return maxLengthCheck;
    },
  };

  const {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    handleSubmit,
  } = useFormValidation(
    {
      name: initialValues.name || '',
      unique_name: initialValues.unique_name || '',
      greeting: initialValues.greeting || '',
      external_platform: initialValues.external_platform || '',
      external_project_key: initialValues.external_project_key || '',
      external_board_id: initialValues.external_board_id || '',
      jira_url: initialValues.jira_url || '',
      jira_email: initialValues.jira_email || '',
      jira_api_token: initialValues.jira_api_token || '',
      trello_api_key: initialValues.trello_api_key || '',
      trello_token: initialValues.trello_token || '',
    },
    validationRules
  );

  const externalPlatformOptions = [
    { value: '', label: t('boards.form.noExternal') || 'No external platform' },
    { value: 'jira', label: 'Jira' },
    { value: 'trello', label: 'Trello' },
  ];

  return (
    <Form onSubmit={handleSubmit(onSubmit)}>
      <FormGroup
        label={t('boards.form.name') || 'Board Name'}
        error={touched.name && errors.name}
        required
        htmlFor="name"
      >
        <Input
          type="text"
          id="name"
          name="name"
          value={values.name}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.name && errors.name}
          placeholder={t('boards.form.namePlaceholder') || 'Enter board name'}
        />
      </FormGroup>

      <FormGroup
        label={t('boards.form.uniqueName') || 'Unique Name'}
        error={touched.unique_name && errors.unique_name}
        required
        helpText={t('boards.form.uniqueNameHelp') || 'URL-friendly identifier for this board (max 255 characters)'}
        htmlFor="unique_name"
      >
        <Input
          type="text"
          id="unique_name"
          name="unique_name"
          value={values.unique_name}
          onChange={handleChange}
          onBlur={handleBlur}
          error={touched.unique_name && errors.unique_name}
          placeholder={t('boards.form.uniqueNamePlaceholder') || 'e.g., support-tickets'}
          maxLength={255}
        />
      </FormGroup>

      <FormGroup
        label={t('boards.form.greeting') || 'Greeting Message'}
        error={touched.greeting && errors.greeting}
        helpText={t('boards.form.greetingHelp') || 'Optional message shown when ticket is submitted'}
        htmlFor="greeting"
      >
        <Textarea
          id="greeting"
          name="greeting"
          value={values.greeting}
          onChange={handleChange}
          onBlur={handleBlur}
          rows={3}
          placeholder={t('boards.form.greetingPlaceholder') || 'Thank you for your submission...'}
        />
      </FormGroup>

      <FormGroup
        label={t('boards.form.externalPlatform') || 'External Platform'}
        error={touched.external_platform && errors.external_platform}
        helpText={t('boards.form.externalPlatformHelp') || 'Optionally sync tickets with Jira or Trello'}
        htmlFor="external_platform"
      >
        <Select
          id="external_platform"
          name="external_platform"
          value={values.external_platform}
          onChange={handleChange}
          onBlur={handleBlur}
          options={externalPlatformOptions}
        />
      </FormGroup>

      {/* Jira Configuration */}
      {values.external_platform === 'jira' && (
        <>
          <FormGroup
            label={t('boards.form.jiraUrl') || 'Jira URL'}
            error={touched.jira_url && errors.jira_url}
            htmlFor="jira_url"
          >
            <Input
              type="url"
              id="jira_url"
              name="jira_url"
              value={values.jira_url}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.jira_url && errors.jira_url}
              placeholder="https://your-domain.atlassian.net"
            />
          </FormGroup>

          <FormGroup
            label={t('boards.form.jiraEmail') || 'Jira Email'}
            error={touched.jira_email && errors.jira_email}
            htmlFor="jira_email"
          >
            <Input
              type="email"
              id="jira_email"
              name="jira_email"
              value={values.jira_email}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.jira_email && errors.jira_email}
              placeholder="your-email@example.com"
            />
          </FormGroup>

          <FormGroup
            label={t('boards.form.jiraApiToken') || 'Jira API Token'}
            error={touched.jira_api_token && errors.jira_api_token}
            htmlFor="jira_api_token"
          >
            <Input
              type="password"
              id="jira_api_token"
              name="jira_api_token"
              value={values.jira_api_token}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.jira_api_token && errors.jira_api_token}
              placeholder="Enter API token"
            />
          </FormGroup>

          <FormGroup
            label={t('boards.form.jiraProjectKey') || 'Jira Project Key'}
            error={touched.external_project_key && errors.external_project_key}
            htmlFor="external_project_key"
          >
            <Input
              type="text"
              id="external_project_key"
              name="external_project_key"
              value={values.external_project_key}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.external_project_key && errors.external_project_key}
              placeholder="PROJ"
            />
          </FormGroup>
        </>
      )}

      {/* Trello Configuration */}
      {values.external_platform === 'trello' && (
        <>
          <FormGroup
            label={t('boards.form.trelloApiKey') || 'Trello API Key'}
            error={touched.trello_api_key && errors.trello_api_key}
            htmlFor="trello_api_key"
          >
            <Input
              type="text"
              id="trello_api_key"
              name="trello_api_key"
              value={values.trello_api_key}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.trello_api_key && errors.trello_api_key}
              placeholder="Enter API key"
            />
          </FormGroup>

          <FormGroup
            label={t('boards.form.trelloToken') || 'Trello Token'}
            error={touched.trello_token && errors.trello_token}
            htmlFor="trello_token"
          >
            <Input
              type="password"
              id="trello_token"
              name="trello_token"
              value={values.trello_token}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.trello_token && errors.trello_token}
              placeholder="Enter token"
            />
          </FormGroup>

          <FormGroup
            label={t('boards.form.trelloBoardId') || 'Trello Board ID'}
            error={touched.external_board_id && errors.external_board_id}
            htmlFor="external_board_id"
          >
            <Input
              type="text"
              id="external_board_id"
              name="external_board_id"
              value={values.external_board_id}
              onChange={handleChange}
              onBlur={handleBlur}
              error={touched.external_board_id && errors.external_board_id}
              placeholder="Enter board ID"
            />
          </FormGroup>
        </>
      )}

      <div className="d-flex gap-2 justify-content-end mt-4">
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          {initialValues.id ? t('common.save') : t('common.create')}
        </Button>
      </div>
    </Form>
  );
};

export default BoardForm;
